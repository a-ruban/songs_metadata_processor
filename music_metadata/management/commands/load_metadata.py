from django.core.management.base import BaseCommand

from bmat.song_metadata_processor import SongMetadataProcessor


class Command(BaseCommand):
    help = 'Load songs-metadata from .csv file to DB'

    def add_arguments(self, parser):
        parser.add_argument('input_file', nargs=1, type=str)

    def handle(self, *args, **options):
        file_name = options.get('input_file')[0]
        metadata_processor = SongMetadataProcessor(file_name)
        metadata_processor.write_metadata_to_db()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully load info about songs')
        )
