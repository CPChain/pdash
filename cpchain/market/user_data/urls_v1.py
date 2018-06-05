from django.conf.urls import url

from cpchain.market.user_data.views import *

urlpatterns = [
    url(r'^pull_all/$', PullUserInfoAPIView.as_view(), name='pull_user_data'),
    url(r'^uploaded_file/add/$', UploadFileInfoAddAPIView.as_view(), name='uploaded_file_add'),
    url(r'^uploaded_file/update/$', UploadFileInfoUpdateAPIView.as_view(), name='uploaded_file_update'),
    url(r'^uploaded_file/delete/$', UploadFileInfoDeleteAPIView.as_view(), name='uploaded_file_delete'),
    url(r'^buyer_file/add/$', BuyerFileInfoAddAPIView.as_view(), name='buyer_file_add'),
    url(r'^buyer_file/update/$', BuyerFileInfoUpdateAPIView.as_view(), name='buyer_file_update'),
    url(r'^buyer_file/delete/$', BuyerFileInfoDeleteAPIView.as_view(), name='buyer_file_delete'),

    url(r'^latest_version/$', UserInfoVersionAPIView.as_view(), name='latest_version'),
    url(r'^tag/search/$', ProductTagSearchAPIView.as_view(), name='tag_search'),
    url(r'^tag/add/$', ProductTagAddAPIView.as_view(), name='tag_add'),
    url(r'^bookmark/search/$', BookmarkSearchAPIView.as_view(), name='bookmark_search'),
    url(r'^bookmark/add/$', BookmarkAddAPIView.as_view(), name='bookmark_add'),

]
