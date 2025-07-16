from django.urls import path
from .views import (
    ProcessHospitalRequestsView,
    home,
    DonorRegisterView,
    DonationCreateView,
    HospitalRequestCreateView,
    HospitalRequestListView,
)

urlpatterns = [
    path("", home, name="home"),
    path("donor/register/", DonorRegisterView.as_view(), name="donor-register"),
    path("donation/", DonationCreateView.as_view(), name="donation"),
    path(
        "hospital/request/",
        HospitalRequestCreateView.as_view(),
        name="hospital-request",
    ),
    path(
        "hospital/requests/",
        HospitalRequestListView.as_view(),
        name="hospital-requests",
    ),
    # urls.py
    path(
        "process-requests/",
        ProcessHospitalRequestsView.as_view(),
        name="process-requests",
    ),
]
