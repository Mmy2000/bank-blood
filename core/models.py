from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
from datetime import timedelta


class Donor(models.Model):
    national_id = models.CharField(
        max_length=14, unique=True, validators=[MinLengthValidator(14)]
    )
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} ({self.national_id})"


class Donation(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    virus_test_result = models.BooleanField()
    accepted = models.BooleanField(default=False)

    def is_eligible(self):
        last = (
            Donation.objects.filter(donor=self.donor, accepted=True)
            .order_by("-date")
            .first()
        )
        if last and (timezone.now().date() - last.date) < timedelta(days=90):
            return False, "Donation too soon (less than 3 months)."
        if not self.virus_test_result:
            return False, "Virus test is positive."
        return True, "Eligible"

    def __str__(self):
        return f"Donation #{self.id} by {self.donor.name}"


class BloodStock(models.Model):
    BLOOD_TYPES = [("A", "A"), ("B", "B"), ("O", "O"), ("AB", "AB")]

    donation = models.OneToOneField(Donation, on_delete=models.CASCADE)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)
    city = models.CharField(max_length=100)
    expiration_date = models.DateField()

    def __str__(self):
        return f"{self.blood_type} in {self.city} (Expires: {self.expiration_date})"


class HospitalRequest(models.Model):
    URGENCY = [("Immediate", "Immediate"), ("Urgent", "Urgent"), ("Normal", "Normal")]

    blood_type = models.CharField(max_length=3, choices=BloodStock.BLOOD_TYPES)
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=URGENCY)
    quantity = models.PositiveIntegerField()
    fulfilled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.status} request for {self.blood_type} in {self.city}"
