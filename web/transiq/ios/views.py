from django.shortcuts import render

# Create your views here.
def place_order(request):
    return render(request, 'ios/place_order.html')


def login(request):
    return render(request, 'ios/login.html')

def policy(request):
    return render(request,'ios/policy.html')
