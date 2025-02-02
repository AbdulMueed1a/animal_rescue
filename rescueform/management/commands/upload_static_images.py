from django.core.management.base import BaseCommand
from django.conf import settings
from rescueform.models import submission
from rescueform.views import upload_image_to_imgur
import os

class Command(BaseCommand):
    help = "Upload images from a static folder to Imgur and update submission records."

    def add_arguments(self, parser):
        parser.add_argument(
            '--folder',
            type=str,
            help='Relative path from the static folder to the images.',
            default='your_image_folder'
        )

    def handle(self, *args, **options):
        static_dir = os.path.join(settings.BASE_DIR, 'static')
        image_folder = options['folder']
        images_path = os.path.join(static_dir, image_folder)

        if not os.path.isdir(images_path):
            self.stdout.write(self.style.ERROR(f"Folder not found: {images_path}"))
            return

        for filename in os.listdir(images_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                file_path = os.path.join(images_path, filename)
                self.stdout.write(f"Uploading {file_path}...")

                try:
                    with open(file_path, 'rb') as image_file:
                        imgur_url = upload_image_to_imgur(image_file)

                    if imgur_url:
                        # Update the corresponding submission record
                        try:
                            subm = submission.objects.get(image_name=filename)
                            subm.imgur_url = imgur_url
                            subm.save()
                            self.stdout.write(self.style.SUCCESS(f"Updated submission for {filename} with Imgur URL."))
                        except submission.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"No submission found for {filename}."))
                    else:
                        self.stdout.write(self.style.ERROR(f"Imgur upload failed for: {filename}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing {filename}: {e}"))
