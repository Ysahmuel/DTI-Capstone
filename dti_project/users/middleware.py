from .models import ActivityLog
from .utils import log_activity
import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

logger = logging.getLogger(__name__)

class ActivityLoggingMiddleware:
    """Middleware to log important page views (exclude repetitive navigation)"""
    
    # Pages to exclude from logging (reduces noise)
    EXCLUDED_PATHS = [
        '/static/',
        '/media/',
        '/api/health/',
        '/__debug__/',
        '/favicon.ico',
    ]
    
    # Only log these specific important pages
    TRACKED_PAGES = {
        '/dashboard/': 'Dashboard',
        '/settings/': 'Account Settings',
        '/profile/': 'Profile',
        '/documents/': 'Documents',
        '/payments/': 'Payments',
        '/staff/': 'Staff Accounts',
        '/admin/': 'Admin Panel',
    }
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Skip excluded paths
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return response
        
        # Only log for authenticated users, GET requests, and successful responses
        if request.user.is_authenticated and request.method == 'GET' and response.status_code == 200:
            # Only log if path matches tracked pages
            should_log = any(request.path.startswith(page) for page in self.TRACKED_PAGES.keys())
            
            if should_log:
                page_name = self._get_page_name(request)
                log_activity(
                    user=request.user,
                    action=f"Accessed {page_name}",
                    action_type=ActivityLog.ActionType.VIEW_PAGE,
                    ip=self._get_client_ip(request),
                    user_agent=request.META.get("HTTP_USER_AGENT")
                )
        
        return response
    
    def _get_page_name(self, request):
        """Extract readable page name from URL"""
        path = request.path
        
        for pattern, name in self.TRACKED_PAGES.items():
            if path.startswith(pattern):
                return name
        
        return path.strip('/').split('/')[-1].replace('-', ' ').title() or 'Home'
    
    def _get_client_ip(self, request):
        """Get client IP from request, handling proxies"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SessionExpiryLoggingMiddleware(MiddlewareMixin):
    """Log when user sessions expire"""
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Check if session is about to expire
            session_timeout = 30 * 60  # 30 minutes in seconds
            last_activity = request.session.get('_last_activity')
            
            if last_activity:
                time_since_last = timezone.now().timestamp() - last_activity
                if time_since_last > session_timeout:
                    # Session expired
                    log_activity(
                        user=request.user,
                        action=f"Session expired due to inactivity",
                        action_type=ActivityLog.ActionType.SESSION_EXPIRED,
                        ip=request.META.get("REMOTE_ADDR"),
                        user_agent=request.META.get("HTTP_USER_AGENT"),
                        visibility="private"
                    )
            
            # Update last activity time
            request.session['_last_activity'] = timezone.now().timestamp()
        
        return None