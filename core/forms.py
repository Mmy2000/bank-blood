from django import forms
from .models import Donor, Donation, HospitalRequest


class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ["national_id", "name", "city", "email"]
        


class DonationForm(forms.Form):
    donor = forms.ModelChoiceField(queryset=Donor.objects.all())
    virus_test_result = forms.BooleanField(
        required=False, label="Virus Test Result (Negative = Checked)"
    )
    blood_type = forms.ChoiceField(
        choices=[("A", "A"), ("B", "B"), ("O", "O"), ("AB", "AB")]
    )


class HospitalRequestForm(forms.ModelForm):
    class Meta:
        model = HospitalRequest
        fields = ["blood_type", "city", "status", "quantity"]
