
from django.views.generic import CreateView, FormView, ListView
from django.shortcuts import redirect,render
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib import messages
from .models import Donor, Donation, BloodStock, HospitalRequest
from .forms import DonorForm, DonationForm, HospitalRequestForm

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
        donation = Donation.objects.create(
            donor=donor,
            virus_test_result=virus_test_result,
        )
        is_valid, reason = donation.is_eligible()

        if not is_valid:
            donation.accepted = False
            donation.save()
            send_mail(
                "Donation Rejected",
                f"Dear {donor.name},\nYour donation was rejected: {reason}",
                "noreply@bloodbank.com",
                [donor.email],
            )
            messages.warning(self.request, f"Donation rejected: {reason}")
        else:
            donation.accepted = True
            donation.save()
            # Sample blood stock creation logic
            BloodStock.objects.create(
                donation=donation,
                blood_type=form.cleaned_data["blood_type"],
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
