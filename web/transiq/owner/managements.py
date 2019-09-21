import pandas as pd
from django.contrib.admin.utils import NestedObjects
from django.contrib.auth.models import User
from django.db.models import Q

from driver.models import Driver
from owner.models import Vehicle, Owner
from restapi.serializers.owner import VehicleSerializer
from team.models import ManualBooking


def vehicle_booking_data():
    data = []
    for vehicle in Vehicle.objects.all():
        bookings = vehicle.manualbooking_set.exclude(booking_status='cancelled')
        data.append([
            vehicle.id,
            vehicle.vehicle_number,
            bookings.count() if bookings.exists() else 0,
            bookings.first().shipment_date if bookings.exists() else '',
            bookings.last().shipment_date if bookings.exists() else '',
            vehicle.created_on
        ])
    df = pd.DataFrame(data=data, columns=['ID', 'Vehicle Number', 'Total Number of Bookings', 'First Booking Date',
                                          'Last Booking Date', 'Created on'])
    df.to_excel('vehicles booking data.xlsx', index=False)


def delete_data():
    for user in User.objects.filter(
            id__in=[602, 654, 616, 611, 577, 613, 424, 580, 598, 574, 590, 579, 581, 588, 575, 645, 626, 576, 597, 615,
                    637, 50, 13, 181, 592, 552, 559, 189, 163, 641, 620, 558, 591, 638, 634, 636, 627, 642, 628, 612,
                    609, 560, 630, 646, 639, 578, 551, 564, 606, 38, 46, 583, 589, 557, 656, 655, 633, 566, 610,
                    595, 562, 619, 596, 607, 649, 650, 644, 586, 198, 553, 197, 568, 572, 561, 632, 622, 608, 621, 605,
                    569, 618, 617, 570, 640, 402, 584, 593, 624, 603, 623, 582, 550, 635, 563, 601, 585, 600, 652, 27,
                    565, 614, 599, 648, 464, 555, 554, 567, 643, 604, 629, 631, 556, 653, 571, 587, 573, 15, 14]):
        # for user in User.objects.filter(username='roku'):
        collector = NestedObjects(using='default')  # or specific database
        collector.collect([user])
        to_delete = collector.nested()
        print(to_delete, user.profile.name, user.profile.phone)


def get_vehicle_details(vehicle_id=267):
    instance = Vehicle.objects.get(id=vehicle_id)
    vehicle_docs = [{'id': doc.id, 'url': doc.s3_upload.public_url(), 'document_category': doc.document_category,
                     'document_category_display': doc.get_document_category_display(),
                     'thumb_url': doc.s3_upload.public_url(),
                     'bucket': doc.s3_upload.bucket,
                     'folder': doc.s3_upload.folder,
                     'uuid': doc.s3_upload.uuid,
                     'filename': doc.s3_upload.filename,
                     'validity': None,
                     } for doc in
                    instance.vehicle_files.exclude(deleted=True).exclude(s3_upload=None)]
    if isinstance(instance.owner, Owner):
        owner_docs = [{'id': doc.id, 'url': doc.s3_upload.public_url(), 'document_category': doc.document_category,
                       'document_category_display': doc.get_document_category_display(),
                       'thumb_url': doc.s3_upload.public_url(),
                       'bucket': doc.s3_upload.bucket,
                       'folder': doc.s3_upload.folder,
                       'uuid': doc.s3_upload.uuid,
                       'filename': doc.s3_upload.filename,
                       'validity': None,
                       } for doc in
                      instance.owner.owner_files.exclude(s3_upload=None)]
    else:
        owner_docs = []
    if isinstance(instance.driver, Driver):
        driver_docs = [{'id': doc.id, 'url': doc.s3_upload.public_url(), 'document_category': doc.document_category,
                        'document_category_display': doc.get_document_category_display(),
                        'thumb_url': doc.s3_upload.public_url(),
                        'bucket': doc.s3_upload.bucket,
                        'folder': doc.s3_upload.folder,
                        'uuid': doc.s3_upload.uuid,
                        'filename': doc.s3_upload.filename,
                        'validity': None,
                        } for doc in
                       instance.driver.driver_files.exclude(s3_upload=None)]
    else:
        driver_docs = []
    return vehicle_docs + owner_docs + driver_docs


def vehicle_details_test():
    for vehicle in Vehicle.objects.all():
        print(get_vehicle_details(vehicle.id))


def test_vehicle_serializer():
    vehicle = Vehicle.objects.get(id=4191)
    vehicle_serializer = VehicleSerializer(vehicle)
    print(vehicle_serializer.data)


def vehicle_data():
    vehicles = ManualBooking.objects.filter(source_office_id=2).exclude(
        Q(booking_status='cancelled') | Q(deleted=True)).values_list('vehicle_id', flat=True)
    data = []
    for vehicle in Vehicle.objects.filter(id__in=list(set(vehicles))):
        data.append(vehicle.vehicle_number)
        for booking in ManualBooking.objects.filter(source_office_id=2).exclude(
                Q(booking_status='cancelled') | Q(deleted=True)).filter(vehicle=vehicle):
            data.append(booking.owner.get_name() if booking.owner else None)
            data.append(booking.owner.get_phone() if booking.owner else None)
            data.append(booking.supplier.get_name() if booking.supplier else None)
            data.append(booking.supplier.get_phone() if booking.supplier else None)
            data.append(booking.booking_id)
            data.append('\n'.join(booking.lr_numbers.values_list('lr_number',flat=True)))
            data.append(booking.get_pod_status_display())
            data.append(booking.pod_date)
