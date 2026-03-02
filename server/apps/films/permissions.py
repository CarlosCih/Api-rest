from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Permiso personalizado para que solo el dueño pueda modificar/eliminar 
    """
    
    def has_object_permission(self, request, view, obj):
        # Lee el permisono de solo lectura para métodos seguros
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user
        
        # Escribe permisos para métodos no seguros
        return obj.user == request.user