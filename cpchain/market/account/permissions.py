from rest_framework import permissions

from .models import Token
import logging

logger = logging.getLogger(__name__)


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

        logger.debug('public_key:%s,token:%s' % (public_key, token))
        # FIXME if obj has attr public_key, test if object.public_key == public_key
        return Token.objects.filter(public_key__exact=public_key).filter(key__exact=token).exists()


class AlreadyLoginUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return self.check_permission(request)

    def has_object_permission(self, request, view, obj):
        return self.check_permission(request)

    def check_permission(self, request):
        public_key = request.META.get('HTTP_MARKET_KEY', 'unknown')
        token = request.META.get('HTTP_MARKET_TOKEN', 'unknown')

        logger.debug('public_key:%s,token:%s' % (public_key,token))
        return Token.objects.filter(public_key__exact=public_key).filter(key__exact=token).exists()


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return self.check_permission(request)

    def has_object_permission(self, request, view, obj):
        return self.check_permission(request)

    def check_permission(self, request):
        public_key = request.META.get('HTTP_MARKET_KEY', 'unknown')
        token = request.META.get('HTTP_MARKET_TOKEN', 'unknown')
        # FIXME if obj has attr public_key, test if object.public_key == public_key

        logger.debug('public_key:%s,token:%s' % (public_key,token))
        return Token.objects.filter(public_key__exact=public_key).filter(key__exact=token).exists()
