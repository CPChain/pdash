from rest_framework.views import APIView

from cpchain.market.account.permissions import AlreadyLoginUser
from cpchain.market.market.utils import *
from cpchain.market.user_data.models import UploadFileInfo, BuyerFileInfo, UserInfoVersion, ProductTag, Bookmark
from cpchain.market.user_data.serializers import BuyerFileInfoUpdateSerializer
from cpchain.market.user_data.serializers import UploadFileInfoSerializer, UserInfoVersionSerializer, \
    BuyerFileInfoSerializer, ProductTagSerializer, BookmarkSerializer

logger = logging.getLogger(__name__)


def increase_data_version(public_key):
    try:
        user_version = UserInfoVersion.objects.get(public_key=public_key)
        user_version.version = user_version.version + 1
    except UserInfoVersion.DoesNotExist:
        user_version = UserInfoVersion(version=1, public_key=public_key)
        logger.debug("user_version:%s" % user_version.version)
    user_version.save()
    return user_version.version


class UploadFileInfoAddAPIView(APIView):
    """
    API endpoint that allows add UploadFileInfo.
    """
    queryset = UploadFileInfo.objects.all()
    serializer_class = UploadFileInfoSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def post(self, request):
        public_key = get_header(self.request)
        logger.info("public_key:%s" % public_key)

        data = request.data
        data['public_key'] = public_key
        logger.info("data:%s" % data)
        serializer = UploadFileInfoSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            user_version = increase_data_version(public_key)
            serializer.save()
            return create_success_data_response({'version': user_version})


class UploadFileInfoUpdateAPIView(APIView):
    """
    API endpoint that allows add UploadFileInfo.
    """
    queryset = UploadFileInfo.objects.all()
    serializer_class = UploadFileInfoSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def post(self, request):
        public_key = get_header(self.request)
        logger.info("public_key:%s" % public_key)

        data = request.data
        data['public_key'] = public_key
        # public_key + client_id -->market_hash + is_published
        info = UploadFileInfo.objects.get(public_key=public_key, client_id=data['client_id'])

        # update profile
        serializer = UploadFileInfoSerializer(info, data=data)
        if serializer.is_valid(raise_exception=True):
            user_version = increase_data_version(public_key)
            serializer.update(instance=info, validated_data=data)
            return create_success_data_response({'version': user_version})


class UploadFileInfoDeleteAPIView(APIView):
    """
    API endpoint that allows delete UploadFileInfo.
    """
    queryset = UploadFileInfo.objects.all()
    serializer_class = UploadFileInfoSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def post(self, request):
        public_key = get_header(self.request)
        logger.info("public_key:%s" % public_key)

        data = request.data
        data['public_key'] = public_key
        deleted, rows_count = UploadFileInfo.objects.filter(
            public_key=public_key, client_id=data['client_id']
        ).delete()
        logger.info("deleted:%i" % deleted)
        logger.info(rows_count)

        if deleted:
            user_version = increase_data_version(public_key)
            return create_success_data_response({'version': user_version})


class PullUserInfoAPIView(APIView):
    """
    API endpoint that allows pull user info (UploadFileInfo,BuyerFileInfo) by owner.
    """
    queryset = UploadFileInfo.objects.all()
    serializer_class = UploadFileInfoSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def get(self, request):
        public_key = get_header(self.request)
        logger.info("public_key:%s" % public_key)

        upload_file_queryset = UploadFileInfo.objects.filter(public_key=public_key)
        upload_file_serializer = UploadFileInfoSerializer(upload_file_queryset, many=True)

        buyer_file_queryset = BuyerFileInfo.objects.filter(public_key=public_key)
        buyer_file_serializer = BuyerFileInfoSerializer(buyer_file_queryset, many=True)

        upload_file_list = upload_file_serializer.data
        buyer_file_list = buyer_file_serializer.data
        all_data = {"public_key": public_key, "upload_files": upload_file_list, "buyer_files": buyer_file_list}
        return create_success_data_response(all_data)


class BuyerFileInfoAddAPIView(APIView):
    """
    API endpoint that allows add BuyerFileInfo.
    """
    queryset = BuyerFileInfo.objects.all()
    serializer_class = BuyerFileInfoSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def post(self, request):
        public_key = get_header(self.request)
        logger.info("public_key:%s" % public_key)

        data = request.data
        data['public_key'] = public_key
        logger.info("data:%s" % data)

        serializer = BuyerFileInfoSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user_version = increase_data_version(public_key)
            serializer.save()
            return create_success_data_response({'version': user_version})


class BuyerFileInfoUpdateAPIView(APIView):
    """
    API endpoint that allows add BuyerFileInfo.
    """
    queryset = BuyerFileInfo.objects.all()
    serializer_class = BuyerFileInfoUpdateSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def post(self, request):
        public_key = get_header(self.request)
        logger.info("public_key:%s" % public_key)

        data = request.data
        logger.info("data:%s" % data)

        info = BuyerFileInfo.objects.get(order_id=data['order_id'])

        # update profile
        serializer = BuyerFileInfoUpdateSerializer(info, data=data)
        if serializer.is_valid(raise_exception=True):
            user_version = increase_data_version(public_key)
            serializer.update(instance=info, validated_data=data)
            return create_success_data_response({'version': user_version})


class BuyerFileInfoDeleteAPIView(APIView):
    """
    API endpoint that allows delete BuyerFileInfo.
    """
    queryset = BuyerFileInfo.objects.all()
    serializer_class = BuyerFileInfoUpdateSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def post(self, request):
        public_key = get_header(self.request)
        logger.info("public_key:%s" % public_key)

        data = request.data
        logger.info("data:%s" % data)

        deleted, _ = BuyerFileInfo.objects.filter(order_id=data['order_id']).delete()

        if deleted:
            user_version = increase_data_version(public_key)
            return create_success_data_response({'version': user_version})


class UserInfoVersionAPIView(APIView):
    """
    API endpoint that allows query latest user data version by owner.
    """
    queryset = UserInfoVersion.objects.all()
    serializer_class = UserInfoVersionSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def get(self, request):
        public_key = get_header(self.request)
        logger.info("public_key:%s" % public_key)
        params = request.query_params
        version = params.get('version')
        logger.debug("version is %s" % version)

        try:
            user_version = UserInfoVersion.objects.get(public_key=public_key)
            return create_success_data_response({'version': user_version.version})
        except UserInfoVersion.DoesNotExist:
            logger.info("user version not found for %s" % public_key)
            return create_success_data_response({'version': 0})


class ProductTagSearchAPIView(APIView):
    """
    API endpoint that allows query product tag data by owner.
    """
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def get(self, request):
        public_key = get_header(self.request)
        logger.info("public_key:%s" % public_key)
        tag_queryset = ProductTag.objects.all()
        tag_serializer = ProductTagSerializer(tag_queryset, many=True)
        return create_success_data_response({'tags': tag_serializer.data})


class ProductTagAddAPIView(APIView):
    """
    API endpoint that allows query product tag data by owner.
    """
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def post(self, request):
        data = request.data
        logger.info("data:%s" % data)

        serializer = ProductTagSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return create_success_response()


class BookmarkSearchAPIView(APIView):
    """
    API endpoint that allows query bookmark data by owner.
    """
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def get(self, request):
        public_key = get_header(self.request)
        logger.info("public_key:%s" % public_key)

        bookmark_queryset = Bookmark.objects.filter(public_key=public_key)
        bookmark_serializer = BookmarkSerializer(bookmark_queryset, many=True)
        bookmark_list = bookmark_serializer.data
        return create_success_data_response({'bookmarks': bookmark_list})


class BookmarkAddAPIView(APIView):
    """
    API endpoint that allows add bookmark.
    """
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = (AlreadyLoginUser,)

    @ExceptionHandler
    def post(self, request):
        data = request.data
        logger.info("data:%s" % data)
        serializer = BookmarkSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return create_success_data_response({'bookmark': serializer.data})
