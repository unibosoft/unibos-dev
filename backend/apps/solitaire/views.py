"""
Solitaire Web Views
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import uuid

from .models import SolitaireSession, SolitaireStatistics, SolitairePlayer, SolitaireGameSession, SolitaireActivity
from .game import SolitaireGame, hash_password, verify_password


def get_or_create_player(request):
    """Get or create a SolitairePlayer for the current user/session"""
    # Get IP address
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if ip_address:
        ip_address = ip_address.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
    
    # Get user agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
    
    # Get or create player
    if request.user.is_authenticated:
        # For authenticated users
        player, created = SolitairePlayer.objects.get_or_create(
            user=request.user,
            defaults={
                'session_key': request.session.session_key or str(uuid.uuid4()),
                'ip_address': ip_address,
                'user_agent': user_agent,
                'is_anonymous': False,
                'display_name': request.user.username
            }
        )
    else:
        # For anonymous users (future public access)
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key
        
        player, created = SolitairePlayer.objects.get_or_create(
            session_key=session_key,
            ip_address=ip_address,
            defaults={
                'user_agent': user_agent,
                'is_anonymous': True,
                'display_name': f'Guest_{session_key[:8]}'
            }
        )
    
    # Update last seen and IP if changed
    if not created:
        player.last_seen = timezone.now()
        if player.ip_address != ip_address:
            player.ip_address = ip_address
        if player.user_agent != user_agent:
            player.user_agent = user_agent
        player.save()
    
    return player


@login_required
def solitaire_game(request):
    """Main solitaire game view"""
    # Track player
    player = get_or_create_player(request)
    player.total_sessions += 1
    player.save()
    
    # Get or create active session
    session = SolitaireSession.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    game_session = None
    
    if not session:
        # Create new session
        session_id = str(uuid.uuid4())
        session = SolitaireSession.objects.create(
            user=request.user,
            session_id=session_id
        )
        
        # Initialize new game
        game = SolitaireGame()
        game.new_game()
        session.save_game_state(game.to_dict())
        
        # Create game session for tracking
        game_session = SolitaireGameSession.objects.create(
            player=player,
            session_id=session_id,
            game_state=game.to_dict(),
            browser_info={
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'screen_width': request.GET.get('screen_width', ''),
                'screen_height': request.GET.get('screen_height', '')
            }
        )
        
        # Log activity
        SolitaireActivity.objects.create(
            session=game_session,
            action='start',
            details={'ip': player.ip_address}
        )
    else:
        # Find existing game session
        try:
            game_session = SolitaireGameSession.objects.get(
                session_id=session.session_id,
                player=player
            )
        except SolitaireGameSession.DoesNotExist:
            # Create new game session for existing session
            game_session = SolitaireGameSession.objects.create(
                player=player,
                session_id=session.session_id,
                game_state=session.get_game_state()
            )
    
    context = {
        'session_id': session.session_id,
        'game_state': session.get_game_state(),
        'is_locked': bool(session.lock_password),
        'player_id': player.id,
        'is_anonymous': player.is_anonymous
    }
    
    # Use the new v3.1 template with proper spacing
    from django.views.decorators.cache import never_cache
    from django.utils import timezone
    
    context['cache_buster'] = int(timezone.now().timestamp() * 1000)
    context['solitaire_version'] = 'v3.1'
    context['spacing_version'] = '2px-18px-fixed'
    
    response = render(request, 'web_ui/solitaire_v31.html', context)
    
    # Add cache-busting headers
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response


@login_required
@csrf_exempt
def solitaire_api(request, action):
    """API endpoint for game actions"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        
        session = SolitaireSession.objects.get(
            session_id=session_id,
            user=request.user
        )
        
        # Load game state
        game = SolitaireGame()
        game.from_dict(session.get_game_state())
        
        result = {'success': False}
        
        if action == 'draw':
            game.draw_from_stock()
            result['success'] = True
            
        elif action == 'select':
            pile_type = data.get('pile_type')
            pile_index = data.get('pile_index', 0)
            card_index = data.get('card_index', -1)
            game.select_card(pile_type, pile_index, card_index)
            result['success'] = True
            
        elif action == 'move':
            pile_type = data.get('pile_type')
            pile_index = data.get('pile_index', 0)
            result['success'] = game.move_selected_to(pile_type, pile_index)
            
        elif action == 'auto':
            result['success'] = game.auto_move_to_foundation()
            
        elif action == 'undo':
            result['success'] = game.undo()
            
        elif action == 'new_game':
            game.new_game()
            session.is_won = False
            result['success'] = True
            
        elif action == 'save_time':
            game.time = data.get('time', 0)
            result['success'] = True
        
        elif action == 'win':
            # Mark game as won
            game.score = data.get('final_score', game.score)
            game.moves = data.get('final_moves', game.moves)
            game.time = data.get('final_time', game.time)
            result['success'] = True
        
        elif action == 'lock':
            password = data.get('password')
            if password:
                session.set_minimize_lock(hash_password(password))
                result['success'] = True
        
        elif action == 'unlock':
            password = data.get('password')
            if session.verify_lock(hash_password(password)):
                session.lock_password = None
                session.save()
                result['success'] = True
            else:
                result['error'] = 'Incorrect password'
        
        # Save game state
        session.save_game_state(game.to_dict())
        
        # Update game session tracking
        player = get_or_create_player(request)
        try:
            game_session = SolitaireGameSession.objects.get(
                session_id=session.session_id,
                player=player
            )
            # Update game session with current state
            game_session.game_state = game.to_dict()
            game_session.moves_count = game.moves
            game_session.score = game.score
            game_session.time_played = game.time
            game_session.save()
            
            # Log activity based on action
            if action == 'move' and result['success']:
                SolitaireActivity.objects.create(
                    session=game_session,
                    action='move',
                    details={'from': data.get('pile_type', ''), 'to': pile_type if 'pile_type' in locals() else ''}
                )
            elif action == 'new_game':
                # End old session and create new one
                game_session.end_session(won=False)
                
                # Create new game session
                new_session_id = str(uuid.uuid4())
                session.session_id = new_session_id
                session.save()
                
                game_session = SolitaireGameSession.objects.create(
                    player=player,
                    session_id=new_session_id,
                    game_state=game.to_dict()
                )
                SolitaireActivity.objects.create(
                    session=game_session,
                    action='start',
                    details={'ip': player.ip_address}
                )
        except SolitaireGameSession.DoesNotExist:
            # Create game session if it doesn't exist
            game_session = SolitaireGameSession.objects.create(
                player=player,
                session_id=session.session_id,
                game_state=game.to_dict(),
                moves_count=game.moves,
                score=game.score,
                time_played=game.time
            )
        
        # Check for win (both from auto-detection and explicit win action)
        if (game.is_won() or action == 'win') and not session.is_won:
            session.is_won = True
            session.save()
            
            # Mark game session as won
            game_session.end_session(won=True)
            SolitaireActivity.objects.create(
                session=game_session,
                action='win',
                details={'score': game.score, 'moves': game.moves, 'time': game.time}
            )
            
            # Update statistics
            stats, _ = SolitaireStatistics.objects.get_or_create(user=request.user)
            stats.games_won += 1
            stats.current_win_streak += 1
            if stats.current_win_streak > stats.best_win_streak:
                stats.best_win_streak = stats.current_win_streak
            stats.total_score += game.score
            if game.score > stats.highest_score:
                stats.highest_score = game.score
            if not stats.fastest_win or game.time < stats.fastest_win:
                stats.fastest_win = game.time
            if not stats.fewest_moves_win or game.moves < stats.fewest_moves_win:
                stats.fewest_moves_win = game.moves
            stats.save()
        
        result['game_state'] = game.to_dict()
        return JsonResponse(result)
        
    except SolitaireSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def solitaire_stats(request):
    """View player statistics"""
    stats, _ = SolitaireStatistics.objects.get_or_create(user=request.user)
    
    # Get recent sessions
    recent_sessions = SolitaireSession.objects.filter(
        user=request.user
    ).order_by('-last_played')[:10]
    
    context = {
        'stats': stats,
        'recent_sessions': recent_sessions
    }
    
    return render(request, 'solitaire/stats.html', context)