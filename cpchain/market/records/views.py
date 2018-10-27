from rest_framework import viewsets, mixins
from rest_framework.response import Response
from django.db.models import Q


from cpchain.market.records.serializers import Record, RecordSerializer

class RecordViewSet(mixins.ListModelMixin,
                    viewsets.GenericViewSet):

    queryset = Record.objects.all()
    serializer_class = RecordSerializer

    def list(self, request):
        address = request.query_params.get('address')
        qs = Record.objects.filter().order_by('-date')
        if address:
            qs = qs.filter(Q(to=address) | Q(frm=address))
        serializer = RecordSerializer(qs, many=True)
        return Response(data=serializer.data)
