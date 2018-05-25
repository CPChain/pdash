from rest_framework import permissions

from .models import Token
import logging

logger = logging.getLogger(__name__)


class AlreadyLoginUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return self.check_permission(request)

    def has_object_permission(self, request, view, obj):
        return self.check_permission(request)

    def check_permission(self, request):
        public_key = request.META.get('HTTP_MARKET_KEY', 'unknown')
        token = request.META.get('HTTP_MARKET_TOKEN', 'unknown')
        logger.debug('public_key:%s,token:%s' % (public_key,token))
        if public_key is None:
            return False
        return Token.objects.filter(public_key__exact=public_key).filter(key__exact=token).exists()
