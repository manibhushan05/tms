from django.shortcuts import render

# Create your views here.
def new_booking(request):
    return render(request,'transporter/new_booking.html')
