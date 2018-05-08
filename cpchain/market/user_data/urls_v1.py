from django.conf.urls import url

from cpchain.market.user_data.views import *

urlpatterns = [
    url(r'^pull_all/$', PullUserInfoAPIViewSet.as_view(), name='pull_user_data'),
    url(r'^uploaded_file/$', UploadFileInfoAPIViewSet.as_view(), name='uploaded_file'),
    url(r'^buyer_file/$', BuyerFileInfoAPIViewSet.as_view(), name='buyer_file'),
    url(r'^latest_version/$', UserInfoVersionAPIViewSet.as_view(), name='latest_version'),
]