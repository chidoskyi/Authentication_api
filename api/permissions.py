from rest_framework.permissions import BasePermission # type: ignore
from .models import APIKey

class HasAPIKeyPermission(BasePermission):
    """
    Permission class to check if the user has a valid API key.
    """
    def has_permission(self, request, view):
        api_key = request.headers.get("X-API-Key") or request.GET.get("api_key")
        if not api_key:
            return False  # Deny access if no API key provided
        
        # Check if the API key is valid
        try:
            key = APIKey.objects.get(key=api_key, is_active=True)
            return True  # Grant access if the key exists and is active
        except APIKey.DoesNotExist:
            return False  # Deny access if the key is invalid
