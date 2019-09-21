from django.contrib import admin

from enquiry.models import DailyRateEnquiry, EnquiryForm, ContactUsLandingPage


class ContactUsLandingPageAdmin(admin.ModelAdmin):
    list_filter = ['created_on']
    list_display = ['id','name','phone','message','created_on']
    search_fields = ('id','name','phone','message')
    actions = ['delete_selected']


admin.site.register(DailyRateEnquiry)
admin.site.register(EnquiryForm)
admin.site.register(ContactUsLandingPage,ContactUsLandingPageAdmin)
