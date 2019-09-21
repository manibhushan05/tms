
from rest_framework import serializers
from django.db import IntegrityError
from fms.models import APP_PLATFORM, ANDROID_APPS, APP_VERSION_UPGRADE_TYPE, MobileAppVersions


class MobileAppVersionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    app_platform = serializers.ChoiceField(allow_null=True, choices=APP_PLATFORM, required=True)
    app_name = serializers.ChoiceField(allow_null=True, choices=ANDROID_APPS, required=True)
    app_version = serializers.CharField(max_length=5, allow_null=True, required=True)
    comment = serializers.CharField(max_length=100, allow_null=True, required=False)
    upgrade_type = serializers.ChoiceField(allow_null=True, choices=APP_VERSION_UPGRADE_TYPE, required=False)

    def create(self, validated_data):
        try:
            app_version = MobileAppVersions.objects.create(**validated_data)
        except (IntegrityError, MobileAppVersions.DoesNotExist):
            raise serializers.ValidationError({'status': 'failure', 'msg': 'MobileAppVersions could not be created'})
        return app_version

    def update(self, instance, validated_data):
        instance.app_platform = validated_data['app_platform']
        instance.app_name = validated_data['app_name']
        instance.app_version = validated_data['app_version']
        instance.comment = validated_data['comment']
        instance.upgrade_type = validated_data['upgrade_type']
        instance.save()
        return instance

    @staticmethod
    def check_update_need(validated_data):
        mobile_app_version = MobileAppVersions.objects.filter(app_name=validated_data['app_name'],
                                                              app_platform=validated_data['app_platform']).\
            exclude(deleted=True).order_by('-created_on').first()

        if not mobile_app_version:
            raise serializers.ValidationError({'status': 'failure', 'msg': 'Mobile app {} version not found'.
                                              format(validated_data['app_name'])})
        if mobile_app_version.app_version == str(validated_data['app_version']):
            force_upgrade = False
            recommend_upgrade = False
        else:
            if mobile_app_version.upgrade_type == 'force':
                force_upgrade = True
                recommend_upgrade = False
            else:
                recommend_upgrade = True
                force_upgrade = False

        return {'status': 'success', 'msg': 'App version data',
                'data': {
                    'forceUpgrade': force_upgrade,
                    'recommendUpgrade': recommend_upgrade,
                    'latest_version': mobile_app_version.app_version
                }}

