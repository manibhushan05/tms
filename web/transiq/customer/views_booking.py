from api.decorators import api_post
from customer.booking_helper import do_booking_vendor_request, do_booking_save, do_add_vendor, do_delete_vendor
from customer.decorators import authenticated_user


@api_post
@authenticated_user
def booking_vendor_request(request):
    return do_booking_vendor_request(request)


@api_post
@authenticated_user
def booking_save(request):
    return do_booking_save(request)


@api_post
@authenticated_user
def add_vendor(request):
    return do_add_vendor(request)


@api_post
@authenticated_user
def delete_vendor(request):
    return do_delete_vendor(request)

