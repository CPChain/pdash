from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from cpchain.market.main.models import Carousel, HotTag, Promotion
from cpchain.market.main.serializers import CarouselQuerySerializer, HotTagSerializer, PromotionSerializer, \
    CarouselAddSerializer
from cpchain.market.market.utils import *

logger = logging.getLogger(__name__)


class CarouselQueryAPIView(APIView):
    """
    API endpoint that allows query Carousel
    """
    queryset = Carousel.objects.all()
    serializer_class = CarouselQuerySerializer
    permission_classes = (AllowAny,)

    @ExceptionHandler
    def get(self, request):
        carousel_queryset = Carousel.objects.filter(status=1)[0:3]
        carousel_serializer = CarouselQuerySerializer(carousel_queryset, many=True)
        return create_success_data_response(carousel_serializer.data)


class CarouselAddAPIView(APIView):
    """
    API endpoint that allows add Carousel
    """
    queryset = Carousel.objects.all()
    serializer_class = CarouselAddSerializer
    permission_classes = (AllowAny,)

    @ExceptionHandler
    def post(self, request):
        data = request.data
        logger.info("data:%s" % data)

        serializer = CarouselAddSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return create_success_response()


class PromotionQueryAPIView(APIView):
    """
    API endpoint that allows query Promotion
    """
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = (AllowAny,)

    @ExceptionHandler
    def get(self, request):
        query_set = Promotion.objects.filter(status=1)
        serializer = PromotionSerializer(query_set, many=True)
        return create_success_data_response(serializer.data)


class PromotionAddAPIView(APIView):
    """
    API endpoint that allows query Promotion
    """
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = (AllowAny,)

    @ExceptionHandler
    def post(self, request):
        data = request.data
        logger.info("data:%s" % data)

        serializer = PromotionSerializer(data=data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return create_success_response()


class HotTagQueryAPIView(APIView):
    """
    API endpoint that allows query Carousel
    """
    queryset = HotTag.objects.all()
    serializer_class = HotTagSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        query_set = HotTag.objects.filter(status=1)
        serializer = HotTagSerializer(query_set, many=True)
        return create_success_data_response(serializer.data)


class HotTagAddAPIView(APIView):
    """
    API endpoint that allows query Carousel
    """
    queryset = HotTag.objects.all()
    serializer_class = HotTagSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        logger.info("data:%s" % data)

        serializer = HotTagSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return create_success_response()
