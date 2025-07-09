from django.contrib import admin
from .models import Donation,Donor,HospitalRequest,BloodStock
# Register your models here.
admin.site.register(Donation)
admin.site.register(Donor)
admin.site.register(HospitalRequest)
admin.site.register(BloodStock)