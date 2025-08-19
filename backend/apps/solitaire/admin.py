"""
Solitaire Admin Configuration
"""

from django.contrib import admin
from .models import SolitaireSession, SolitaireMove, SolitaireStatistics


@admin.register(SolitaireSession)
class SolitaireSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'score', 'moves_count', 'is_active', 'is_won', 'last_played']
    list_filter = ['is_active', 'is_won', 'created_at']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['created_at', 'last_played']
    
    fieldsets = [
        ('Session Info', {
            'fields': ['user', 'session_id', 'is_active', 'is_won']
        }),
        ('Game State', {
            'fields': ['stock_pile', 'waste_pile', 'foundation_piles', 'tableau_piles'],
            'classes': ['collapse']
        }),
        ('Statistics', {
            'fields': ['moves_count', 'score', 'game_time']
        }),
        ('Security', {
            'fields': ['last_minimize', 'lock_password']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'last_played']
        })
    ]


@admin.register(SolitaireMove)
class SolitaireMoveAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'move_number', 'from_pile', 'to_pile', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['session__session_id']
    readonly_fields = ['timestamp']


@admin.register(SolitaireStatistics)
class SolitaireStatisticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'games_played', 'games_won', 'win_rate', 'highest_score', 'best_win_streak']
    search_fields = ['user__username']
    readonly_fields = ['last_updated']
    
    fieldsets = [
        ('User', {
            'fields': ['user']
        }),
        ('Game Stats', {
            'fields': ['games_played', 'games_won', 'total_score', 'highest_score', 'total_time_played']
        }),
        ('Streaks', {
            'fields': ['current_win_streak', 'best_win_streak']
        }),
        ('Records', {
            'fields': ['fastest_win', 'fewest_moves_win']
        }),
        ('Metadata', {
            'fields': ['last_updated']
        })
    ]