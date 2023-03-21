from django.core.files.storage import FileSystemStorage
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import os


class CustomStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIA_LOCATION
    default_acl = settings.MEDIA_DEFAULT_ACL
    file_overwrite = True
