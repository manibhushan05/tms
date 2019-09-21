from api.models import S3Upload


def update_is_verified_data():
    S3Upload.objects.update(verified=True, is_valid=True)
