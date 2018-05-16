from django.http import JsonResponse
from rest_framework.views import APIView
from cpchain.market.account.permissions import AlreadyLoginUser
from cpchain.market.market.utils import *
from cpchain.market.user_data.models import UploadFileInfo, BuyerFileInfo, UserInfoVersion, ProductTag, Bookmark
from cpchain.market.user_data.serializers import UploadFileInfoSerializer, UserInfoVersionSerializer, \
    BuyerFileInfoSerializer, ProductTagSerializer, BookmarkSerializer

logger = logging.getLogger(__name__)

PUBLIC_KEY = "public_key"
VERIFY_CODE = "code"
TIMEOUT = 1000


def create_invalid_response():
    return JsonResponse({'status': 0, "message": "invalid request."})


def create_success_response():
    return JsonResponse({'status': 1, 'message': 'success'})


def increase_data_version(public_key):
    try:
        user_version = UserInfoVersion.objects.get(public_key=public_key)
        user_version.version = user_version.version + 1
    except UserInfoVersion.DoesNotExist:
        user_version = UserInfoVersion(version=1, public_key=public_key)
        logger.debug("user_version:%s" % user_version.version)
    user_version.save()
    return user_version.version


class UploadFileInfoAPIView(APIView):
    """
    API endpoint that allows add UploadFileInfo.
    """
    queryset = UploadFileInfo.objects.all()
    serializer_class = UploadFileInfoSerializer
    permission_classes = (AlreadyLoginUser,)

    def post(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("public_key:%s" % public_key)

        if public_key is None:
            return create_invalid_response()

        data = request.data
        data['public_key'] = public_key
        logger.info("data:%s" % data)
        serializer = UploadFileInfoSerializer(data=data)

        try:
            if serializer.is_valid(raise_exception=True):
                user_version = increase_data_version(public_key)
                serializer.save()
                return JsonResponse({'status': 1, 'message': 'success', 'data': {'version': user_version}})
        except:
            logger.exception("save UploadFileInfo error")

        return create_invalid_response()


class PullUserInfoAPIView(APIView):
    """
    API endpoint that allows pull user info (UploadFileInfo,BuyerFileInfo) by owner.
    """
    queryset = UploadFileInfo.objects.all()
    serializer_class = UploadFileInfoSerializer
    permission_classes = (AlreadyLoginUser,)

    def get(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("public_key:%s" % public_key)

        upload_file_queryset = UploadFileInfo.objects.filter(public_key=public_key)
        upload_file_serializer = UploadFileInfoSerializer(upload_file_queryset,many=True)

        buyer_file_queryset = BuyerFileInfo.objects.filter(public_key=public_key)
        buyer_file_serializer = BuyerFileInfoSerializer(buyer_file_queryset, many=True)

        upload_file_list = upload_file_serializer.data
        buyer_file_list = buyer_file_serializer.data
        all_data = {"public_key": public_key, "upload_files": upload_file_list, "buyer_files": buyer_file_list}
        return JsonResponse({'status': 1, 'message': 'success', 'data': all_data})


class BuyerFileInfoAPIView(APIView):
    """
    API endpoint that allows add BuyerFileInfo.
    """
    queryset = BuyerFileInfo.objects.all()
    serializer_class = BuyerFileInfoSerializer
    permission_classes = (AlreadyLoginUser,)

    def post(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("public_key:%s" % public_key)

        if public_key is None:
            return create_invalid_response()

        data = request.data
        data['public_key'] = public_key
        logger.info("data:%s" % data)

        serializer = BuyerFileInfoSerializer(data=data)

        try:
            if serializer.is_valid(raise_exception=True):
                user_version = increase_data_version(public_key)
                serializer.save()
                return JsonResponse({'status': 1, 'message': 'success', 'data': {'version': user_version}})
        except:
            logger.exception("save BuyerFileInfo error")

        return create_invalid_response()


class UserInfoVersionAPIView(APIView):
    """
    API endpoint that allows query latest user data version by owner.
    """
    queryset = UserInfoVersion.objects.all()
    serializer_class = UserInfoVersionSerializer
    permission_classes = (AlreadyLoginUser,)

    def get(self, request):

        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("public_key:%s" % public_key)
        params = request.query_params
        version = params.get('version')
        logger.debug("version is %s" % version)

        try:
            user_version = UserInfoVersion.objects.get(public_key=public_key)
            return JsonResponse({'status': 1, 'message': 'success', 'data': {'version': user_version.version}})
        except UserInfoVersion.DoesNotExist:
            logger.info("user version not found for %s" % public_key)
            return JsonResponse({'status': 1, 'message': 'success', 'data': {'version': 0}})


class ProductTagSearchAPIView(APIView):
    """
    API endpoint that allows query product tag data by owner.
    """
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    permission_classes = (AlreadyLoginUser,)

    def get(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("public_key:%s" % public_key)

        try:
            tag_queryset = ProductTag.objects.all()
            tag_serializer = ProductTagSerializer(tag_queryset, many=True)
            tag_list = tag_serializer.data
            return JsonResponse({'status': 1, 'message': 'success', 'data': {'tags': tag_list}})
        except:
            logger.exception("ProductTag not found for %s" % public_key)
            return create_invalid_response()


class ProductTagAddAPIView(APIView):
    """
    API endpoint that allows query product tag data by owner.
    """
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    permission_classes = (AlreadyLoginUser,)

    def post(self, request):
        data = request.data
        logger.info("data:%s" % data)

        try:
            serializer = ProductTagSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse({'status': 1, 'message': 'success'})
        except:
            logger.exception("save ProductTag error")

        return create_invalid_response()


class BookmarkSearchAPIView(APIView):
    """
    API endpoint that allows query bookmark data by owner.
    """
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = (AlreadyLoginUser,)

    def get(self, request):
        public_key = self.request.META.get('HTTP_MARKET_KEY')
        logger.info("public_key:%s" % public_key)

        try:
            bookmark_queryset = Bookmark.objects.filter(public_key=public_key)
            bookmark_serializer = BookmarkSerializer(bookmark_queryset, many=True)
            bookmark_list = bookmark_serializer.data
            return JsonResponse({'status': 1, 'message': 'success', 'data': {'bookmarks': bookmark_list}})
        except:
            logger.info("bookmark not found for %s" % public_key)
            return create_invalid_response()


class BookmarkAddAPIView(APIView):
    """
    API endpoint that allows add bookmark.
    """
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = (AlreadyLoginUser,)

    def post(self, request):
        data = request.data
        logger.info("data:%s" % data)
        try:
            serializer = BookmarkSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse({'status': 1, 'message': 'success','data':{'bookmark':serializer.data}})
        except:
            logger.exception("save Bookmark error")

        return create_invalid_response()
