from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from cpchain.market.account.utils import *
from cpchain.market.main.models import Carousel, HotTag, Promotion
from cpchain.market.main.serializers import CarouselQuerySerializer, HotTagSerializer, PromotionSerializer, \
    CarouselAddSerializer

logger = logging.getLogger(__name__)

def create_invalid_response():
    return JsonResponse({"status": 0, "message": "invalid request."})


def create_success_response():
    return JsonResponse({'status': 1, 'message': 'success'})


class CarouselQueryAPIView(APIView):
    """
    API endpoint that allows query Carousel
    """
    queryset = Carousel.objects.all()
    serializer_class = CarouselQuerySerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        carousel_queryset = Carousel.objects.filter(status=1)[0:3]
        carousel_serializer = CarouselQuerySerializer(carousel_queryset, many=True)
        carousel_list = carousel_serializer.data
        return JsonResponse({'status': 1, 'message': 'success', 'data': carousel_list})


class CarouselAddAPIView(APIView):
    """
    API endpoint that allows add Carousel
    """
    queryset = Carousel.objects.all()
    serializer_class = CarouselAddSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        logger.info("data:%s" % data)

        serializer = CarouselAddSerializer(data=data)

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse({'status': 1, 'message': 'success'})
        except:
            logger.exception("save Carousel error")

        return create_invalid_response()


class PromotionQueryAPIView(APIView):
    """
    API endpoint that allows query Promotion
    """
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        query_set = Promotion.objects.filter(status=1)
        serializer = PromotionSerializer(query_set, many=True)
        data_list = serializer.data
        return JsonResponse({'status': 1, 'message': 'success', 'data': data_list})


class PromotionAddAPIView(APIView):
    """
    API endpoint that allows query Promotion
    """
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        logger.info("data:%s" % data)

        serializer = PromotionSerializer(data=data)

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse({'status': 1, 'message': 'success'})
        except:
            logger.exception("save Promotion error")

        return create_invalid_response()


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
        data_list = serializer.data
        return JsonResponse({'status': 1, 'message': 'success', 'data': data_list})


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

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return JsonResponse({'status': 1, 'message': 'success'})
        except:
            logger.exception("save HotTag error")

        return create_invalid_response()
