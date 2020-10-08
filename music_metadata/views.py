from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.mixins import ListModelMixin

from music_metadata.models import Song
from music_metadata.serializers import SongSerializer


class SongDetailsView(RetrieveAPIView):
    serializer_class = SongSerializer

    def get_object(self):
        iswc = self.kwargs.get('iswc')
        return Song.objects.get(iswc=iswc)


class SongMetadataEnrichmentView(GenericAPIView, ListModelMixin):
    serializer_class = SongSerializer

    def get_queryset(self):
        iswcs = self.request.data.get('iswcs')
        if iswcs:
            return Song.objects.filter(iswc__in=iswcs)

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
