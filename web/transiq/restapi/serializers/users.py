from rest_framework import serializers
from rest_framework.fields import IntegerField
from rest_framework.validators import UniqueValidator

from restapi.models import UserCategory


class UserCategorySerializer(serializers.Serializer):
    id = IntegerField(read_only=True)
    category = serializers.CharField(max_length=15, required=True, trim_whitespace=True,
                                     validators=[UniqueValidator(queryset=UserCategory.objects.all())])

    def create(self, validated_data):
        # create user category
        user_category = UserCategory.objects.create(
            category=validated_data['category'],
        )
        return user_category

    def update(self, instance, validated_data):
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance

    @staticmethod
    def is_instance_user_category(validated_data):
        try:
            user_category = UserCategory.objects.filter(category=validated_data['category']).exclude(deleted=True)
        except UserCategory.DoesNotExist:
            return False
        if not user_category:
            return False
        else:
            return True
