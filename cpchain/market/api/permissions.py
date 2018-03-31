from django.db.models import Q
from rest_framework import permissions
from .models import Token


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return self.check_permission(request)

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return self.check_permission(request)
        # return obj.owner.id == request.session.get('user_id')

    def check_permission(self, request):
        public_key = request.META.get('HTTP_MARKET_KEY', 'unknown')
        token = request.META.get('HTTP_MARKET_TOKEN', 'unknown')

        print('public_key:' + str(public_key) + " token:" + str(token))

        return Token.objects.filter(public_key__exact=public_key).filter(key__exact=token).exists()
