from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.models import S3Upload


class S3UploadSerializer(serializers.Serializer):
    id = serializers.IntegerField(label='ID', read_only=True)
    bucket = serializers.CharField(max_length=63)
    folder = serializers.CharField(max_length=150)
    uuid = serializers.CharField(max_length=50, validators=[UniqueValidator(queryset=S3Upload.objects.all())])
    filename = serializers.CharField(max_length=150)
    uploaded = serializers.BooleanField(default=True)
    verified = serializers.BooleanField(required=False)
    is_valid = serializers.BooleanField(required=False)
    deleted = serializers.BooleanField(required=False)
    uploaded_on = serializers.DateTimeField(allow_null=True, required=False)
    deleted_on = serializers.DateTimeField(allow_null=True, required=False)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        instance = S3Upload.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        S3Upload.objects.filter(id=instance.id).update(**validated_data)
        return S3Upload.objects.get(id=instance.id)
