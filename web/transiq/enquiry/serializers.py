from rest_framework import serializers

from enquiry.models import ContactUsLandingPage
from team import tasks


class ContactUsLandingPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUsLandingPage
        fields = '__all__'

    def create(self, validated_data):
        instance = ContactUsLandingPage.objects.create(**validated_data)
        msg = 'Name: {}\nPhone: {}\nEmail ID: {}\n Message{}'.format(instance.name, instance.phone, instance.email,
                                                                     instance.message)
        tasks.landing_page_enquiry.delay(msg)
        return instance

    def update(self, instance, validated_data):
        pass
