from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from fms.models import ANDROID_APPS
from notification.models import MobileDevice
from restapi.helper_api import DATETIME_FORMAT


class MobileDeviceSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    app = serializers.ChoiceField(choices=ANDROID_APPS)
    token = serializers.CharField(max_length=200, validators=[UniqueValidator(queryset=MobileDevice.objects.all())])
    device_id = serializers.CharField(max_length=100)
    active = serializers.BooleanField(required=False)
    created_on = serializers.DateTimeField(read_only=True,format=DATETIME_FORMAT)
    updated_on = serializers.DateTimeField(read_only=True,format=DATETIME_FORMAT)
    deleted = serializers.BooleanField(write_only=True,required=False)
    deleted_on = serializers.DateTimeField(write_only=True,allow_null=True, required=False)
    created_by = serializers.SlugRelatedField(write_only=True,queryset=User.objects.all(), required=False, slug_field="username")
    changed_by = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")
    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="username")

    def create(self, validated_data):
        mobile_device = MobileDevice.objects.create(**validated_data)
        return mobile_device

    def update(self, instance, validated_data):
        pass
