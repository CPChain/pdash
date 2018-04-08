# Register your models here.
from django.contrib import admin

from .models import WalletUser

# Now register the new UserAdmin...
admin.site.register(WalletUser)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
# admin.site.unregister(Group)