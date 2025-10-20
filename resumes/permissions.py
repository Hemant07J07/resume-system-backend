# resumes/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object (or owners of related resume)
    to edit it. Assumes the model instance has either 'owner' attribute (Resume) or
    'resume' attribute (child models).
    """

    def has_object_permission(self, request, view, obj):
        # safe methods allowed to authenticated users (read only)
        if request.method in SAFE_METHODS:
            return True

        owner = getattr(obj, 'owner', None)
        if owner is not None:
            return owner == request.user

        resume = getattr(obj, 'resume', None)
        if resume is not None:
            return resume.owner == request.user

        # default deny
        return False
