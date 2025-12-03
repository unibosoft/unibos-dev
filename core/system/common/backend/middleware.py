"""
Custom middleware for UNIBOS backend
Implements security headers, rate limiting, and request logging
"""

import time
import json
import logging
from typing import Callable
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from core.system.authentication.backend.models import UserSession

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS is handled by Django's SecurityMiddleware in production
        
        # CSP headers (if not in debug mode)
        if not settings.DEBUG:
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data: https:",
                "connect-src 'self' wss: https:",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
            response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log all requests for monitoring and debugging"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            extra={
                'method': request.method,
                'path': request.path,
                'user': getattr(request.user, 'username', 'anonymous'),
                'ip': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
        )
    
    def process_response(self, request, response):
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'status': response.status_code,
                    'duration': f"{duration:.3f}s",
                    'user': getattr(request.user, 'username', 'anonymous'),
                }
            )
            
            # Add timing header
            response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """Global rate limiting middleware"""
    
    def process_request(self, request):
        # Skip rate limiting for certain paths
        exempt_paths = ['/admin/', '/static/', '/media/', '/health/', '/administration/unlock/', '/birlikteyiz/']
        if any(request.path.startswith(path) for path in exempt_paths):
            return None
        
        # Get client identifier
        if request.user.is_authenticated:
            identifier = f"user_{request.user.id}"
            limit = 50000  # Authenticated users: 50000 requests per hour
        else:
            identifier = f"ip_{self.get_client_ip(request)}"
            limit = 10000  # Anonymous users: 10000 requests per hour
        
        # Check rate limit
        cache_key = f"rate_limit_{identifier}"
        requests_count = cache.get(cache_key, 0)
        
        if requests_count >= limit:
            return JsonResponse(
                {
                    'error': 'Rate limit exceeded',
                    'detail': f'Too many requests. Limit: {limit} requests per hour.'
                },
                status=429
            )
        
        # Increment counter
        cache.set(cache_key, requests_count + 1, 3600)  # 1 hour TTL
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class JWTAuthMiddleware:
    """JWT authentication for WebSocket connections"""
    
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        # Get token from query string or headers
        headers = dict(scope.get('headers', []))
        
        # Try to get token from Authorization header
        auth_header = headers.get(b'authorization', b'').decode()
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # Try to get token from query string
            query_string = scope.get('query_string', b'').decode()
            params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
            token = params.get('token', None)
        
        if token:
            try:
                # Validate token
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(token)
                user = await database_sync_to_async(jwt_auth.get_user)(validated_token)
                
                # Update session activity
                session_key = validated_token.get('jti')
                if session_key:
                    await database_sync_to_async(self.update_session_activity)(user, session_key)
                
                # Add user to scope
                scope['user'] = user
            except (InvalidToken, TokenError) as e:
                # Invalid token, set anonymous user
                scope['user'] = AnonymousUser()
        else:
            # No token provided
            scope['user'] = AnonymousUser()
        
        return await self.inner(scope, receive, send)
    
    def update_session_activity(self, user, session_key):
        """Update session last activity"""
        try:
            session = UserSession.objects.get(
                user=user,
                session_key=session_key,
                is_active=True
            )
            session.save(update_fields=['last_activity'])
        except UserSession.DoesNotExist:
            pass


class CorsMiddleware(MiddlewareMixin):
    """Custom CORS middleware for fine-grained control"""
    
    def process_response(self, request, response):
        # This is handled by django-cors-headers, but we can add custom logic here
        # For WebSocket support
        if request.path.startswith('/ws/'):
            origin = request.META.get('HTTP_ORIGIN')
            if origin in settings.CORS_ALLOWED_ORIGINS:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
        
        return response


class HealthCheckMiddleware(MiddlewareMixin):
    """
    Quick health check middleware - bypasses all other middleware.
    Returns immediately for /health/quick/ and /health/live/ paths.
    Other health checks go through the full middleware stack.
    """

    # Paths that bypass the middleware stack
    BYPASS_PATHS = ['/health/quick/', '/health/live/']

    def process_request(self, request):
        if request.path in self.BYPASS_PATHS:
            return JsonResponse({'status': 'ok', 'timestamp': time.time()})
        return None


class NodeIdentityMiddleware(MiddlewareMixin):
    """
    Add node identity information to request context and response headers.
    Enables multi-node architecture by identifying which node handled the request.
    """

    _identity = None

    @classmethod
    def get_identity(cls):
        """Lazy load node identity"""
        if cls._identity is None:
            try:
                from core.base.identity.identity import get_instance_identity
                cls._identity = get_instance_identity()
            except Exception as e:
                logger.warning(f"Failed to load node identity: {e}")
                cls._identity = None
        return cls._identity

    def process_request(self, request):
        """Add node identity to request"""
        identity = self.get_identity()
        if identity:
            request.node_uuid = identity.get_uuid()
            request.node_type = identity.get_node_type().value
        else:
            request.node_uuid = None
            request.node_type = 'unknown'

    def process_response(self, request, response):
        """Add node identity headers to response"""
        identity = self.get_identity()
        if identity:
            response['X-Node-UUID'] = identity.get_uuid()
            response['X-Node-Type'] = identity.get_node_type().value
        return response


class P2PDiscoveryMiddleware(MiddlewareMixin):
    """
    Handle P2P node discovery headers.
    Allows nodes to advertise themselves and discover peers.
    """

    def process_request(self, request):
        """Check for peer discovery requests"""
        # Check if this is a peer discovery request
        if request.META.get('HTTP_X_UNIBOS_DISCOVER') == 'true':
            request.is_peer_discovery = True
        else:
            request.is_peer_discovery = False

        # Extract peer info if provided
        peer_uuid = request.META.get('HTTP_X_PEER_UUID')
        peer_type = request.META.get('HTTP_X_PEER_TYPE')
        if peer_uuid:
            request.peer_uuid = peer_uuid
            request.peer_type = peer_type

    def process_response(self, request, response):
        """Add discovery information to responses"""
        # If this was a discovery request, add node info
        if getattr(request, 'is_peer_discovery', False):
            try:
                from core.base.identity.identity import get_instance_identity
                identity = get_instance_identity()

                response['X-UNIBOS-Node'] = 'true'
                response['X-Node-UUID'] = identity.get_uuid()
                response['X-Node-Type'] = identity.get_node_type().value
                response['X-Node-Hostname'] = identity.identity.hostname

                # Add capabilities summary
                caps = identity.get_capabilities()
                capabilities = []
                if caps.can_run_django:
                    capabilities.append('django')
                if caps.can_run_celery:
                    capabilities.append('celery')
                if caps.can_run_websocket:
                    capabilities.append('websocket')
                response['X-Node-Capabilities'] = ','.join(capabilities)

            except Exception as e:
                logger.warning(f"P2P discovery error: {e}")

        return response


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Enable graceful maintenance mode.
    When enabled, returns 503 for all requests except health checks and admin.
    """

    # Paths that bypass maintenance mode
    EXEMPT_PATHS = [
        '/health/',
        '/admin/',
        '/api/auth/login/',  # Allow login during maintenance
        '/static/',
        '/media/',
    ]

    def process_request(self, request):
        """Check if maintenance mode is active"""
        # Check maintenance mode from cache or settings
        maintenance_mode = cache.get('maintenance_mode', False)

        # Also check settings for static maintenance
        if not maintenance_mode:
            maintenance_mode = getattr(settings, 'MAINTENANCE_MODE', False)

        if maintenance_mode:
            # Check if path is exempt
            if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
                return None

            # Check if user is superuser (allow admin access)
            if hasattr(request, 'user') and request.user.is_authenticated:
                if request.user.is_superuser:
                    return None

            # Get maintenance message
            maintenance_message = cache.get(
                'maintenance_message',
                getattr(settings, 'MAINTENANCE_MESSAGE', 'System is under maintenance. Please try again later.')
            )

            # Get estimated end time
            maintenance_until = cache.get('maintenance_until')

            response_data = {
                'error': 'maintenance',
                'message': maintenance_message,
                'status': 503,
            }

            if maintenance_until:
                response_data['estimated_end'] = maintenance_until

            return JsonResponse(response_data, status=503)

        return None

    @classmethod
    def enable_maintenance(cls, message: str = None, until: str = None):
        """
        Enable maintenance mode

        Args:
            message: Custom maintenance message
            until: Estimated end time (ISO format)
        """
        cache.set('maintenance_mode', True, timeout=None)
        if message:
            cache.set('maintenance_message', message, timeout=None)
        if until:
            cache.set('maintenance_until', until, timeout=None)
        logger.info("Maintenance mode enabled")

    @classmethod
    def disable_maintenance(cls):
        """Disable maintenance mode"""
        cache.delete('maintenance_mode')
        cache.delete('maintenance_message')
        cache.delete('maintenance_until')
        logger.info("Maintenance mode disabled")