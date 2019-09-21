from rest_framework import viewsets, status
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.response import Response

from utils.models import VehicleCategory


class SupplierPageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def create(self, request):
        return Response(template_name='supplier/registration/register-supplier.html')


class DriverPageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def create(self, request):
        return Response(template_name='supplier/registration/register-driver.html', status=status.HTTP_200_OK)


class VehiclePageView(viewsets.ViewSet):
    renderer_classes = (TemplateHTMLRenderer,)

    def create(self, request):
        vehicle_categories = [
            {'id': vehicle_category.id, 'vehicle_type': vehicle_category.vehicle_type,
             'capacity': vehicle_category.capacity}
            for vehicle_category in VehicleCategory.objects.all()
        ]
        body_type_choices = (
            ('open', 'Open'),
            ('closed', 'Closed'),
            ('semi', 'Semi'),
            ('half', 'Half'),
            ('containerized', 'Containerized'),
        )
        gps_enable_choices = (
            ('yes', 'Yes'),
            ('no', 'No')
        )
        return Response(template_name='supplier/registration/register-vehicle.html', status=status.HTTP_200_OK, data={
            'vehicle_categories': vehicle_categories,
            'body_type_choices': body_type_choices,
            'gps_enable_choices': gps_enable_choices
        })
