"""market URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from cpchain.market.main.models import Carousel, HotTag, Promotion

admin.site.register(Carousel)
admin.site.register(HotTag)
admin.site.register(Promotion)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/v1/', include('account.urls_v1')),
    path('product/v1/', include('product.urls_v1')),
    path('user_data/v1/', include('user_data.urls_v1')),
    path('main/v1/', include('main.urls_v1')),
    path('comment/v1/', include('comment.urls_v1')),
]
