from fileupload.models import PODFile
from team.models import ManualBooking


def validate_pod_uploaded(booking):
    if isinstance(booking, ManualBooking):
        return all([PODFile.objects.filter(lr_number=lr) for lr in booking.lr_numbers.all()])
    else:
        return False


