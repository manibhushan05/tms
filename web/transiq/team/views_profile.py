from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.shortcuts import render

from api.decorators import authenticated_user
from api.helper import json_400_incorrect_use, json_error_response, json_401_inactive_user, json_401_wrong_credentials, \
    json_success_response
from api.utils import get_or_none
from authentication.models import Profile
from employee.models import Employee
from team.helper.helper import verify_profile_phone, verify_profile_email
from utils.models import Bank


@authenticated_user
def emp_profile(request):
    emp = get_or_none(Employee, username=User.objects.get(username=request.user.username))
    return render(request=request, template_name='team/employee/emp-profile.html', context={'emp': emp})


@authenticated_user
def change_password_page(request):
    return render(request=request, template_name='team/employee/change-password.html')


def change_password(request):
    old_password = request.POST.get('old_password')
    new_password = request.POST.get('new_password')
    if not old_password or not new_password:
        return json_400_incorrect_use()
    user = get_or_none(User, username=request.user.username)
    if not user:
        return json_error_response('Incorrect Password', status=404)

    if not user.is_active:
        return json_401_inactive_user()

    auth_user = authenticate(username=request.user.username, password=old_password)
    if auth_user is None:
        return json_401_wrong_credentials()
    user.set_password(new_password)
    user.save()
    new_auth_user = authenticate(username=request.user.username, password=new_password)
    auth_login(request, new_auth_user)
    return json_success_response('Password Changed Successfully')


def update_profile_page(request):
    employee = Employee.objects.get(username=User.objects.get(username=request.user.username))
    return render(request=request, template_name='team/employee/update-profile.html', context={'employee': employee})


def update_profile(request):
    phone_status, msg = verify_profile_phone(username=request.user.username, phone=request.POST.get('phone'),
                                             alt_phone=request.POST.get('alt_phone'))
    if phone_status:
        return json_error_response(msg=msg, status=409)
    email_status, msg = verify_profile_email(username=request.user.username, email=request.POST.get('email'),
                                             alt_email=None)
    if email_status:
        return json_error_response(msg=msg, status=409)
    if Employee.objects.filter(pan__iexact=request.POST.get('pan')).exclude(
            username=User.objects.get(username=request.user.username)).exists():
        return json_error_response("PAN Already Exists", status=409)
    if not Bank.objects.filter(account_number=request.POST.get('account_number')).exists():
        return json_error_response("Account Doesn't Exists, Please send your account details at info@aaho.in",
                                   status=404)

    profile = Profile.objects.get(user=User.objects.get(username=request.user.username))
    profile.name = request.POST.get('name')
    profile.phone = request.POST.get('phone')
    profile.alternate_phone = request.POST.get('alt_phone')
    profile.email = request.POST.get('email')
    profile.save()
    employee = Employee.objects.get(username=User.objects.get(username=request.user.username))
    employee.pan = request.POST.get('pan')
    employee.bank = Bank.objects.get(account_number=request.POST.get('account_number'))
    employee.save()
    return json_success_response("Updated Successfully")
