from django.views.generic import CreateView, FormView, ListView
from django.shortcuts import redirect,render
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib import messages
from core.utils import process_requests
from .models import Donor, Donation, BloodStock, HospitalRequest
from .forms import DonorForm, DonationForm, HospitalRequestForm
from django.utils import timezone
from datetime import timedelta
from django.views import View

# Create your views here.


def home(request):
    return render(request, "home.html")


class DonorRegisterView(CreateView):
    model = Donor
    form_class = DonorForm
    template_name = "donor_register.html"
    success_url = reverse_lazy("donation")


class DonationCreateView(FormView):
    form_class = DonationForm
    template_name = "donation.html"
    success_url = reverse_lazy("donation")

    def form_valid(self, form):
        donor = form.cleaned_data["donor"]
        virus_test_result = form.cleaned_data["virus_test_result"]
        blood_type = form.cleaned_data["blood_type"]

        # Check eligibility first
        last = (
            Donation.objects.filter(donor=donor, accepted=True)
            .order_by("-date")
            .first()
        )
        if last and (timezone.now().date() - last.date) < timedelta(days=90):
            reason = "Donation too soon (less than 3 months)."
            send_mail(
                "Donation Rejected",
                f"Dear {donor.name},\nYour donation was rejected: {reason}",
                "noreply@bloodbank.com",
                [donor.email],
            )
            messages.warning(self.request, f"Donation rejected: {reason}")
            return self.form_invalid(form)

        if not virus_test_result:
            reason = "Virus test is positive."
            send_mail(
                "Donation Rejected",
                f"Dear {donor.name},\nYour donation was rejected: {reason}",
                "noreply@bloodbank.com",
                [donor.email],
            )
            messages.warning(self.request, f"Donation rejected: {reason}")
            return self.form_invalid(form)

        # If eligible, create donation and blood stock
        donation = Donation.objects.create(
            donor=donor, virus_test_result=virus_test_result, accepted=True
        )
        send_mail(
            "Donation Accepted",
            f"Dear {donor.name},\nYour donation has been accepted.",
            "noreply@bloodbank.com",
            [donor.email],
        )

        BloodStock.objects.create(
            donation=donation,
            blood_type=blood_type,
            city=donor.city,
            expiration_date=timezone.now().date() + timezone.timedelta(days=42),
        )

        messages.success(self.request, "Donation accepted and added to stock.")
        return super().form_valid(form)


class HospitalRequestCreateView(CreateView):
    model = HospitalRequest
    form_class = HospitalRequestForm
    template_name = "hospital_request.html"
    success_url = reverse_lazy("hospital-requests")


class HospitalRequestListView(ListView):
    model = HospitalRequest
    template_name = "hospital_requests.html"

    def get_queryset(self):
        requests = super().get_queryset().filter(fulfilled=False)
        for req in requests:
            available = BloodStock.objects.filter(
                blood_type=req.blood_type,
                city=req.city,
                expiration_date__gte=timezone.now().date(),
            )[: req.quantity]

            if available.count() >= req.quantity:
                for b in available:
                    b.delete()  # Remove from stock
                req.fulfilled = True
                req.save()
        return HospitalRequest.objects.all()


class ProcessHospitalRequestsView(View):
    def get(self, request):
        result = process_requests()
        messages.success(request, result)
        return redirect(reverse("hospital-requests"))
