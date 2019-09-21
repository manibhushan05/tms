from django.contrib.auth.models import User
from django.core.mail.message import EmailMessage
from django.test import Client

from api.helper import generate_random_password
from employee.models import Employee


def send_random_generated_password():
    employee = Employee.objects.exclude(status='inactive').values('username__username', 'username__profile__email')
    for emp in employee:
        password = generate_random_password(12)
        msg = 'Please login to your account with following credentials and change password.\n\nusername: %s\npassword: %s' % (
            emp['username__username'], password)
        # print msg
        user = User.objects.get(username=emp['username__username'])
        user.set_password(raw_password=password)
        user.save()
        email = EmailMessage(to=[emp['username__profile__email']], subject='new password', body=msg)
        email.send()


def django_test():
    client = Client()
    response = client.get('/team/dashboard/')
    print(response.status_code)
