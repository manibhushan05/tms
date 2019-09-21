import json

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api.helper import json_success_response, json_401_inactive_user, json_401_wrong_credentials, \
    json_400_incorrect_use, json_error_response
from api.utils import get_or_none, to_int
from .models import ServerErrorMessage


@csrf_exempt
def login_android(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))
        user = authenticate(username=data['username'], password=data['password'])
        if user is not None:
            return HttpResponse('success')
        return HttpResponse('unsuccess')


def login_web(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username, password)

        if not username or not password:
            return json_400_incorrect_use()
        user = get_or_none(User, username=username.lower())
        if not user:
            return json_error_response(
                "The email address or phone number that you've entered doesn't match any account.", status=404)
        if not user.is_active:
            return json_401_inactive_user()
        user = authenticate(username=username.lower(), password=password)
        if user is None:
            return json_401_wrong_credentials()

        auth_login(request, user)
        if any(g.name == 'sme' for g in request.user.groups.all()):
            return json_success_response('sme')
        elif any(g.name == 'supplier' for g in request.user.groups.all()):
            return json_success_response('supplier')
        elif any(g.name == 'ios' for g in request.user.groups.all()):
            return json_success_response('ios')
        elif any(g.name.startswith('emp_group4') for g in request.user.groups.all()):
            return json_success_response('emp_group4')
        elif any(g.name.startswith('emp') for g in request.user.groups.all()):
            return json_success_response('team')
        elif any(g.name.startswith('m_emp') for g in request.user.groups.all()):
            return json_success_response('m_emp')
        elif request.user.is_superuser or request.user.is_staff:
            return json_success_response('admin')
        else:
            return json_success_response('others')
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        pass


def reset_password(request):
    if request.method == 'POST':
        username = request.user.username
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        user = authenticate(username=username, password=old_password)
        if user is not None:
            u = User.objects.get(username=username)
            u.set_password(new_password)
            u.save()
            user = authenticate(username=username, password=new_password)
            auth_login(request, user)
            messages.success(request, "Password has been reset ")
            return HttpResponseRedirect('/company/settings')
        else:
            messages.error(request, "Password reset has been unsuccessful.")
            return HttpResponseRedirect('/company/settings')


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/login/')


def bad_request(request):
    return render(request, 'page_400.html', status=400)


def permission_denied(request):
    return render(request, 'page_403.html', status=403)


# HTTP Error 404
def page_not_found(request):
    return render(request, 'page_404.html', status=404)


# HTTP Error 500
def server_error(request):
    return render(request, 'page_500.html', status=500)


def server_error_message(request):
    ServerErrorMessage.objects.create(
        error_type=request.POST.get('error_type'),
        message=request.POST.get('message'),
        username=request.user.username,
    )
    if request.user.username is not None:
        logout(request)
    return HttpResponseRedirect('/')
