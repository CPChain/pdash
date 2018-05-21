from django.conf.urls import url

from cpchain.market.user_data.views import *

urlpatterns = [
    url(r'^pull_all/$', PullUserInfoAPIView.as_view(), name='pull_user_data'),
    url(r'^uploaded_file/add/$', UploadFileInfoAddAPIView.as_view(), name='add_uploaded_file'),
    url(r'^uploaded_file/update/$', UploadFileInfoUpdateAPIView.as_view(), name='update_uploaded_file'),
    url(r'^buyer_file/add/$', BuyerFileInfoAddAPIView.as_view(), name='add_buyer_file'),
    url(r'^buyer_file/update/$', BuyerFileInfoUpdateAPIView.as_view(), name='update_buyer_file'),

    url(r'^latest_version/$', UserInfoVersionAPIView.as_view(), name='latest_version'),
    url(r'^tag/search/$', ProductTagSearchAPIView.as_view(), name='tag'),
    url(r'^tag/add/$', ProductTagAddAPIView.as_view(), name='add_tag'),
    url(r'^bookmark/search/$', BookmarkSearchAPIView.as_view(), name='bookmark'),
    url(r'^bookmark/add/$', BookmarkAddAPIView.as_view(), name='add_bookmark'),

]
