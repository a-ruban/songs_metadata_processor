from rest_framework import serializers

from music_metadata.models import Song


class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = '__all__'

    contributors = serializers.SerializerMethodField('get_contributor_names')

    def get_contributor_names(self, instance):
        contributor_names = []
        try:
            for contributor in instance.contributors.all():
                contributor_names.append(contributor.name)
            return contributor_names

        except AttributeError:
            return []
