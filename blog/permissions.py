from rest_framework.permissions import BasePermission
from .models import *
class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow read-only access for GET, HEAD, and OPTIONS requests
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        # Check if obj is a Comment (which has a user field)
        if isinstance(obj, Comment):
            # Allow editing or deleting only if the user is the owner of the comment or the post's author
            return obj.user == request.user

        # Check if obj is a Post (which has an author field)
        if isinstance(obj, Post):
            # Allow editing or deleting only if the user is the owner of the post
            return obj.author == request.user

        return False
