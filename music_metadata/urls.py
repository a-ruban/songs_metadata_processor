from django.urls import path

from music_metadata.views import SongDetailsView, SongMetadataEnrichmentView

urlpatterns = [
        path('<str:iswc>/', SongDetailsView.as_view(), name='song_details'),
        path('enrichment/', SongMetadataEnrichmentView.as_view(), name='song_metadata_enrichment'),
    ]