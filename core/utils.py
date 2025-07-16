# utils.py
from math import radians, sin, cos, sqrt, atan2
from .models import HospitalRequest, BloodStock
from django.db.models import Q


def haversine_distance(city1, city2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1 = radians(city1.latitude), radians(city1.longitude)
    lat2, lon2 = radians(city2.latitude), radians(city2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c  # Distance in km


def process_requests():
    requests = HospitalRequest.objects.filter(fulfilled=False)
    if requests.count() < 10:
        return "Not enough requests to process."

    urgency_order = {"Immediate": 1, "Urgent": 2, "Normal": 3}
    requests = sorted(requests, key=lambda r: urgency_order[r.status])

    fulfilled_count = 0

    for request in requests:
        stocks = BloodStock.objects.filter(blood_type=request.blood_type)

        if not stocks.exists():
            continue

        # Sort by distance to request city
        stocks = sorted(
            stocks, key=lambda stock: haversine_distance(request.city, stock.city)
        )

        fulfilled_units = 0
        for stock in stocks:
            if fulfilled_units >= request.quantity:
                break
            stock.delete()  # Remove used stock
            fulfilled_units += 1

        if fulfilled_units == request.quantity:
            request.fulfilled = True
            request.save()
            fulfilled_count += 1

    return f"{fulfilled_count} requests fulfilled out of {len(requests)}."
