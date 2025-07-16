from django.contrib import admin
from .models import Donation,Donor,HospitalRequest,BloodStock,City
# Register your models here.
admin.site.register(Donation)
admin.site.register(Donor)
admin.site.register(HospitalRequest)
admin.site.register(BloodStock)
admin.site.register(City)