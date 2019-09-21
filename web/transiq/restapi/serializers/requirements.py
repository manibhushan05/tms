import re

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
import datetime
from authentication.models import Profile

from rest_framework import serializers
from rest_framework.fields import IntegerField

from api.validators import VEHICLE_NUMBER
from fms.models import QuoteVehicles, Requirement, RequirementVehicleQuote, RequirementQuote, REQ_STATUS
from fms.views_requirement import RDONLY_REQ_STATUS
from restapi.serializers.sme import BasicSmeSerializer
from sme.models import Sme
from api.utils import get_or_none, int_or_none
from supplier.models import Supplier
from utils.models import City, AahoOffice, VehicleCategory


class QuoteVehiclesSerializer(serializers.Serializer):
    id = IntegerField(read_only=True)
    vehicle_no = serializers.CharField(max_length=15, required=True, allow_blank=True, trim_whitespace=True)

    def create(self, validated_data):
        # create quote vehicles
        quote_vehicle, created = QuoteVehicles.objects.get_or_create(vehicle_no=validated_data['vehicle_no'])
        return quote_vehicle

    def update(self, instance, validated_data):
        instance.vehicle_no = validated_data.get('vehicle_no', instance.vehicle_no)
        instance.updated_on = timezone.now()
        instance.save()
        return instance

    @staticmethod
    def check_vehicle_no_pattern(validated_data):
        response = {'status': 'success', 'msg': 'Pattern Match'}
        vehicle_no = validated_data['vehicle_no']
        vehicle_number_pattern = re.compile(VEHICLE_NUMBER[1:-2], re.IGNORECASE)
        if isinstance(vehicle_no, str):
            if vehicle_number_pattern.match(vehicle_no):
                return response
            else:
                response = {'status': 'failure', 'msg': 'Pattern Does Not Match'}
                return response
        else:
            response = {'status': 'failure', 'msg': 'Vehicle No Is Not String'}
            return response


class RequirementVehicleQuoteSerializer(serializers.Serializer):
    quote_vehicle_id = IntegerField(required=True)
    requirement_id = IntegerField(required=True)

    def create(self, validated_data):
        try:
            requirement = Requirement.objects.get(id=validated_data['requirement_id'])
        except Requirement.DoesNotExist:
            raise serializers.ValidationError("Requirement Does Not Exist")
        try:
            quote_veh = QuoteVehicles.objects.get(id=validated_data['quote_vehicle_id'])
        except QuoteVehicles.DoesNotExist:
            raise serializers.ValidationError("QuoteVehicles Does Not Exist")

        requirement_vehicle_quote, created = RequirementVehicleQuote.objects.get_or_create(
            requirement=requirement, quote_vehicle=quote_veh)
        return requirement_vehicle_quote

    def update(self, instance, validated_data):
        try:
            requirement = Requirement.objects.get(id=validated_data['requirement_id'])
        except Requirement.DoesNotExist:
            raise serializers.ValidationError("Requirement Does Not Exist")
        try:
            quote_veh = QuoteVehicles.objects.get(id=validated_data['quote_vehicle_id'])
        except QuoteVehicles.DoesNotExist:
            raise serializers.ValidationError("QuoteVehicles Does Not Exist")
        instance.requirement = requirement
        instance.quote_vehicle = quote_veh
        instance.updated_on = timezone.now()
        instance.save()
        return instance


class RequirementQuoteSerializer(serializers.Serializer):
    id = IntegerField(read_only=True)
    supplier_id = IntegerField(required=True)
    supplier = serializers.SerializerMethodField()
    requirement_vehicle_quote_id = IntegerField(required=True)
    requirement_vehicle_quote = serializers.SerializerMethodField()
    rate = serializers.IntegerField(max_value=99999, required=True)
    status = serializers.CharField(max_length=15, allow_null=True, required=False)

    def create(self, validated_data):
        try:
            supplier = Supplier.objects.get(id=validated_data['supplier_id'])
        except Supplier.DoesNotExist:
            raise serializers.ValidationError("Supplier Does Not Exist")
        try:
            requirement_vehicle_quote = RequirementVehicleQuote(id=validated_data['requirement_vehicle_quote_id'])
        except RequirementVehicleQuote.DoesNotExist:
            raise serializers.ValidationError("RequirementVehicleQuote Does Not Exist")
        requirement_quote = RequirementQuote.objects.create(supplier=supplier,
                                                            requirement_vehicle_quote=requirement_vehicle_quote,
                                                            rate=validated_data['rate'])

        return requirement_quote

    def update(self, instance, validated_data):
        try:
            supplier = Supplier.objects.get(id=validated_data['supplier_id'])
        except Supplier.DoesNotExist:
            raise serializers.ValidationError("Supplier Does Not Exist")
        try:
            requirement_vehicle_quote = RequirementVehicleQuote(id=validated_data['requirement_vehicle_quote_id'])
        except RequirementVehicleQuote.DoesNotExist:
            raise serializers.ValidationError("RequirementVehicleQuote Does Not Exist")
        instance.rate = validated_data.get('rate', instance.rate)
        instance.supplier = supplier
        instance.requirement_vehicle_quote = requirement_vehicle_quote
        instance.updated_on = timezone.now()
        instance.save()
        return instance

    def get_requirement_vehicle_quote(self, obj):
        rvq = get_or_none(RequirementVehicleQuote, id=int_or_none(obj.requirement_vehicle_quote_id))
        if not rvq:
            raise serializers.ValidationError("RequirementVehicleQuote Does Not Exist")
        return {'requirement_id': rvq.requirement.id, 'quote_vehicle_id': rvq.quote_vehicle.id,
                'tonnage': rvq.requirement.tonnage, 'no_of_vehicles': rvq.requirement.no_of_vehicles}

    def get_supplier(self, obj):
        supplier = get_or_none(Supplier, id=int_or_none(obj.supplier_id))
        if not supplier:
            raise serializers.ValidationError("Supplier Does Not Exist")
        profile = Profile.objects.get(user=supplier.user)
        return {'supplier_id': supplier.id, 'supplier_name': profile.name, 'supplier_phone': profile.phone}


class RequirementSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    client_id = serializers.IntegerField(required=True)
    from_shipment_date = serializers.CharField(max_length=10, required=True, trim_whitespace=True)
    to_shipment_date = serializers.CharField(max_length=10, allow_null=True, trim_whitespace=True, required=False)
    from_city_id = serializers.IntegerField(required=True)
    from_city = serializers.SerializerMethodField()
    to_city_id = serializers.IntegerField(required=True)
    to_city = serializers.SerializerMethodField()
    aaho_office_id = serializers.IntegerField(required=True)
    aaho_office = serializers.SerializerMethodField()
    tonnage = serializers.DecimalField(allow_null=True, required=False, max_digits=6, decimal_places=2)
    no_of_vehicles = serializers.IntegerField(max_value=9999, allow_null=True, required=False)
    rate = serializers.IntegerField(max_value=99999, allow_null=True, required=False)
    material = serializers.CharField(max_length=35, allow_null=True)
    type_of_vehicle_id = serializers.IntegerField(max_value=99999, allow_null=True, required=False)
    type_of_vehicle = serializers.SerializerMethodField()
    req_status = serializers.CharField(max_length=35, trim_whitespace=True)
    remark = serializers.CharField(max_length=25, trim_whitespace=False, required=False)
    cancel_reason = serializers.CharField(max_length=75, trim_whitespace=True, required=False)
    client = serializers.SerializerMethodField()
    from_state = serializers.SerializerMethodField()
    to_state = serializers.SerializerMethodField()
    read_only = serializers.SerializerMethodField()
    quotes = serializers.SerializerMethodField()
    client_data = serializers.SerializerMethodField()

    def get_quotes(self, instance):
        quotes = RequirementQuote.objects.filter(requirement_vehicle_quote__requirement__id=instance.id)
        return quotes.count()

    def get_client_data(self, instance):
        if isinstance(instance, Requirement) and isinstance(instance.client, Sme):
            return BasicSmeSerializer(instance.client).data
        return {}

    def create(self, validated_data):
        objects = self.parse_requirement_fields(validated_data, True)
        if objects['status'] == 'failure':
            raise serializers.ValidationError({'status': 'failure', 'msg': objects['msg']})
        objects.pop('status', None)
        try:
            req = Requirement.objects.create(**objects)
        except IntegrityError:
            raise serializers.ValidationError({'status': 'failure', 'msg': 'Inquiry could not be created'})
        return req

    def update(self, instance, validated_data):
        objects = self.parse_requirement_fields(validated_data, False)
        if objects['status'] == 'failure':
            raise serializers.ValidationError({'status': 'failure', 'msg': objects['msg']})

        instance.client = objects['client']
        instance.aaho_office = objects['aaho_office']
        instance.from_shipment_date = objects['from_shipment_date']
        instance.to_shipment_date = objects['to_shipment_date']
        instance.from_city = objects['from_city']
        instance.to_city = objects['to_city']
        instance.tonnage = objects['tonnage']
        instance.no_of_vehicles = objects['no_of_vehicles']
        instance.material = objects['material']
        instance.type_of_vehicle = objects['type_of_vehicle']
        instance.rate = objects['rate']
        instance.remark = objects['remark']
        instance.cancel_reason = objects['cancel_reason']
        instance.changed_by = User.objects.get(username=validated_data['user'].username)
        instance.updated_on = timezone.now()

        if instance.req_status and validated_data['req_status'] == 'open':
            instance.req_status = objects['req_status']
            instance.save(update_fields=['req_status', 'material', 'client', 'aaho_office', 'from_shipment_date',
                                         'to_shipment_date', 'from_city', 'to_city', 'tonnage', 'no_of_vehicles',
                                         'material', 'type_of_vehicle', 'rate', 'remark', 'cancel_reason', 'changed_by',
                                         'updated_on'])

        else:
            instance.req_status = objects['req_status']
            instance.save()
        return instance

    def get_client(self, obj):
        client = get_or_none(Sme, id=int_or_none(obj.client_id))
        if not client:
            raise serializers.ValidationError("Client Does Not Exist")
        return client.get_name()

    def get_from_city(self, obj):
        city = get_or_none(City, id=int_or_none(obj.from_city_id))
        if not city:
            raise serializers.ValidationError("From City Does Not Exist")
        return city.name

    def get_to_city(self, obj):
        city = get_or_none(City, id=int_or_none(obj.to_city_id))
        if not city:
            raise serializers.ValidationError("To City Does Not Exist")
        return city.name

    def get_aaho_office(self, obj):
        aaho_office = get_or_none(AahoOffice, id=int_or_none(obj.aaho_office_id))
        if not aaho_office:
            raise serializers.ValidationError("AahoOffice Does Not Exist")
        return aaho_office.branch_name

    def get_type_of_vehicle(self, obj):
        type_of_vehicle = get_or_none(VehicleCategory, id=int_or_none(obj.type_of_vehicle_id))
        if not type_of_vehicle:
            vehicle_name = ''
        else:
            vehicle_name = type_of_vehicle.name()
        return vehicle_name

    def get_from_state(self, obj):
        city = get_or_none(City, id=int_or_none(obj.from_city_id))
        if not city:
            raise serializers.ValidationError("From City Does Not Exist")
        else:
            return city.state.name if city and city.state else ''

    def get_to_state(self, obj):
        city = get_or_none(City, id=int_or_none(obj.to_city_id))
        if not city:
            raise serializers.ValidationError("To City Does Not Exist")
        else:
            return city.state.name if city and city.state else ''

    def get_read_only(self, obj):
        if obj.req_status in [x[0] for x in RDONLY_REQ_STATUS]:
            rdonly = True
        else:
            rdonly = False
        return rdonly

    def parse_requirement_fields(self, load, created):
        user = load['user']
        data = load
        from_shipment_date = data.get('from_shipment_date', None)
        to_shipment_date = data.get('to_shipment_date', None)
        try:
            present = datetime.datetime.now()
            from_dt = datetime.datetime.strptime(from_shipment_date, '%Y-%m-%d')
            if to_shipment_date:
                to_date = datetime.datetime.strptime(to_shipment_date, '%Y-%m-%d')
                if to_date < from_dt:
                    return {'status': 'failure', 'msg': 'To Date should be greater than From Date'}
                if to_date.date() < present.date() and created:
                    return {'status': 'failure', 'msg': 'To Date should be greater than or equal to Today'}
                if from_dt.date() < present.date() and created:
                    return {'status': 'failure', 'msg': 'From Date should be greater than or equal to Today'}
            elif from_dt.date() < present.date() and created:
                return {'status': 'failure', 'msg': 'From Date should be greater than or equal to Today'}
        except ValueError:
            return {'status': 'failure', 'msg': 'Incorrect date format, should be YYYY-MM-DD'}

        tonnage = data.get('tonnage', None)
        no_of_vehicles = data.get('no_of_vehicles', None)
        material = data.get('material', None)
        rate = data.get('rate', None)

        if not tonnage and not no_of_vehicles:
            return {'status': 'failure', 'msg': 'Enter Either Tonnage or No of Vehicles'}

        if data.get('from_city_id', None) == data.get('to_city_id', None):
            return {'status': 'failure', 'msg': 'From City and To City should be different'}

        client = get_or_none(Sme, id=int_or_none(data.get('client_id')))

        if not isinstance(client, Sme):
            return {'status': 'failure', 'msg': 'Incorrect client '}
        from_city = get_or_none(City, id=data.get('from_city_id', None))
        if not isinstance(from_city, City):
            return {'status': 'failure', 'msg': 'Incorrect from city '}
        to_city = get_or_none(City, id=data.get('to_city_id', None))
        if not isinstance(to_city, City):
            return {'status': 'failure', 'msg': 'Incorrect to city '}
        type_of_vehicle = get_or_none(VehicleCategory, id=int_or_none(data.get('type_of_vehicle_id')))
        aaho_office = get_or_none(AahoOffice, id=data.get('aaho_office_id', None))
        if not isinstance(aaho_office, AahoOffice):
            return {'status': 'failure', 'msg': 'Incorrect Aaho Office'}
        created_by = User.objects.get(username=user.username)
        if tonnage and not no_of_vehicles:
            no_of_vehicles = None
        if no_of_vehicles and not tonnage:
            tonnage = None
        if not rate:
            rate = None
        if not type_of_vehicle:
            type_of_vehicle = None
        else:
            if not isinstance(type_of_vehicle, VehicleCategory):
                return {'status': 'failure', 'msg': 'Incorrect vehicle type'}

        req_status = data.get('req_status', None)
        if req_status not in [x[0] for x in REQ_STATUS]:
            return {'status': 'failure', 'msg': 'Inquiry status is wrong'}
        if req_status == 'lapsed':
            return {'status': 'failure', 'msg': 'Inquiry status should be open/unverified'}

        remark = data.get('remark', None)
        if not remark:
            remark = None

        cancel_reason = data.get('cancel_reason', None)
        if not cancel_reason:
            cancel_reason = None

        objects = {'status': 'success', 'client': client, 'from_shipment_date': from_shipment_date,
                   'to_shipment_date': to_shipment_date, 'from_city': from_city, 'to_city': to_city,
                   'aaho_office': aaho_office, 'tonnage': tonnage,
                   'no_of_vehicles': no_of_vehicles, 'material': material, 'type_of_vehicle': type_of_vehicle,
                   'rate': rate, 'created_by': created_by, 'req_status': req_status, 'remark': remark,
                   'cancel_reason': cancel_reason}
        return objects
