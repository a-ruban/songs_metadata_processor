import csv
import os
import uuid

import django
from django.conf import settings
from django.db.models import Q

if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmat.settings')
    django.setup()

from music_metadata.models import Contributor, Song


class SongMetadataProcessor:
    def __init__(self, input_file_name):
        self.rows_to_write_iswc = dict()
        self.rows_to_write_no_iswc = dict()

        with open(input_file_name, 'r') as input_file:
            self.input_rows = csv.reader(input_file)
            next(self.input_rows)

            rows_without_iswc = []
            rows_with_iswc = []

            for row in self.input_rows:
                new_iswc = row[2]
                new_song_authors = set(row[1].split('|'))
                new_song_title = row[0]
                if new_iswc:
                    rows_with_iswc.append([new_song_title, new_song_authors, new_iswc])
                else:
                    rows_without_iswc.append([new_song_title, new_song_authors, ''])

            self._prepare_rows_with_iswc(rows_with_iswc)
            self._prepare_rows_without_iswc(rows_without_iswc)

    def write_metadata_to_db(self):
        """
        Write metadata to DB  matching and reconciling exisiting rows.
        """
        contributors = self._create_contributors()
        existing_songs_iswc = Song.objects.filter(Q(iswc__in=self.rows_to_write_iswc.keys())).prefetch_related(
            'contributors')

        self._update_existing_songs_iswc(existing_songs_iswc, contributors)

        unique_new_song_titles = set(song.get('title') for song in self.rows_to_write_no_iswc.values())
        existing_songs_no_iswc = Song.objects.filter(title__in=unique_new_song_titles).prefetch_related('contributors')
        self._update_existing_songs_no_iswc(existing_songs_no_iswc, contributors)

        self._write_new_songs(contributors)

    def _write_new_songs(self, contributors):
        songs = []
        for song in self.rows_to_write_iswc.values():
            songs.append(Song(
                title=song.get('title'),
                iswc=song.get('iswc')
            ))
        created_songs = Song.objects.bulk_create(songs)

        for song in self.rows_to_write_iswc.values():
            created_song = \
                list(filter(lambda x: song.get('title') == x.title and song.get('iswc') == x.iswc, created_songs))[0]
            for name in song.get('authors'):
                contributor_id = contributors.get(name)
                if contributor_id:
                    created_song.contributors.add(int(contributor_id))

    def _prepare_rows_with_iswc(self, rows_with_iswc):
        for row in rows_with_iswc:
            new_iswc = row[2]
            new_song_authors = row[1]
            new_song_title = row[0]
            existing_song = self.rows_to_write_iswc.get(new_iswc)
            if not existing_song:
                self.rows_to_write_iswc[new_iswc] = {
                    'title': new_song_title,
                    'authors': new_song_authors,
                    'iswc': new_iswc
                }

            else:
                existing_song_authors = existing_song.get('authors')
                self.rows_to_write_iswc[new_iswc] = {
                    'title': new_song_title if new_song_title else existing_song.get('title'),
                    'authors': new_song_authors.union(existing_song_authors),
                    'iswc': existing_song.get('iswc')
                }

    def _prepare_rows_without_iswc(self, rows_without_iswc):
        for row in rows_without_iswc:
            new_iswc = row[2]
            new_song_authors = row[1]
            new_song_title = row[0]

            song_found = False
            for song in self.rows_to_write_iswc.values():
                if new_song_title == song.get('title') and len(new_song_authors.intersection(song.get('authors'))) > 0:
                    song = {
                        'title': new_song_title if new_song_title else song.get('title'),
                        'authors': new_song_authors.union(song.get('authors')),
                        'iswc': new_iswc if new_iswc else song.get('iswc')
                    }
                    song_found = True
                    break

            if not song_found:
                self.rows_to_write_no_iswc[uuid.uuid4()] = {
                    'title': new_song_title,
                    'authors': new_song_authors,
                    'iswc': new_iswc
                }

    def _create_contributors(self):
        contributor_names = set()
        for song in self.rows_to_write_iswc.values():
            contributor_names = contributor_names.union(song.get('authors'))
        for song in self.rows_to_write_no_iswc.values():
            contributor_names = contributor_names.union(song.get('authors'))

        existing_contributors = Contributor.objects.values(
            'name').distinct()
        existing_contributor_names = set(contributor.get('name') for contributor in existing_contributors)
        contributor_names_to_create = contributor_names.difference(existing_contributor_names)
        created_contributors = Contributor.objects.bulk_create(
            (Contributor(name=contributor_name) for contributor_name in contributor_names_to_create)
        )
        existing_contributors = list(Contributor.objects.filter(name__in=existing_contributor_names))

        return {contributor.name: contributor.id for contributor in created_contributors + existing_contributors}

    def _update_existing_songs_no_iswc(self, existing_songs_no_iswc, contributors):
        for id, new_song in self.rows_to_write_no_iswc.items():
            for song in existing_songs_no_iswc.filter(title=new_song.get('title')):
                if new_song.get('title') == song.title and len(new_song.get('authors').intersection(
                        set(song.contributors.values_list('name', flat=True)))) > 0:
                    authors = new_song.get('authors')
                    if authors:
                        for name in authors:
                            contributor_id = int(contributors.get(name))
                            if contributor_id not in set(song.contributors.values_list('id', flat=True)):
                                new_song.contributors.add(contributor_id)
                    del self.rows_to_write_no_iswc[id]
                    break

    def _update_existing_songs_iswc(self, existing_songs_iswc, contributors):
        for song in existing_songs_iswc:
            new_song = self.rows_to_write_iswc.get(song.iswc)
            if new_song.get('title'):
                song.title = new_song.get('title')

            authors = new_song.get('authors')
            if authors:
                for name in authors:
                    contributor_id = int(contributors.get(name))
                    if contributor_id not in set(song.contributors.values_list('id', flat=True)):
                        song.contributors.add(contributor_id)

            del self.rows_to_write_iswc[song.iswc]
