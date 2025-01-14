from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role != 'staff':
            raise PermissionDenied("Only staff users are allowed to access this view.")
        return True


class IsStaffOrAdminUser(BasePermission):
    def has_permission(self, request, view):
        # Ensure the user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Allow access for staff or admin users
        if request.user.role not in ['staff', 'admin']:
            raise PermissionDenied("Only staff or admin users are allowed to access this view.")
        
        return True

class IsStaffUserAndDepartmentMatch(BasePermission):
    """
    Allows access only to staff users and validates department match.
    """
    def has_object_permission(self, request, view, obj):
        # Ensure the user is a staff member
        if request.user.role != 'staff':
            raise PermissionDenied("You are not a staff user to access this resource.")
        
        # Ensure the user's department matches the object's department
        if request.user.department != obj:
            raise PermissionDenied("You are not the staff of this department.")
        
        return True
    
    
class IsPatientUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role != 'patient':
            raise PermissionDenied("Only staff users are allowed to access this view.")
        return True
    
    
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role != 'admin':
            raise PermissionDenied("Only admin can do this.")
        return True