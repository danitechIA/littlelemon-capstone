import json
from datetime import date as date_cls

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import Menu, Booking


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def menu(request):
    menu_items = Menu.objects.all()
    return render(request, 'menu.html', {'menu_items': menu_items})


def book(request):
    return render(request, 'book.html', {'today': date_cls.today().isoformat()})


def reservations(request):
    return render(request, 'reservations.html', {'today': date_cls.today().isoformat()})


@require_http_methods(['GET', 'POST'])
def bookings(request):
    """
    GET  /bookings            -> JSON list of ALL bookings   (criterion 6)
    GET  /bookings?date=YYYY-MM-DD -> JSON list filtered by date (criterion 10)
    POST /bookings            -> create a booking; rejects a date+slot
                                  that is already taken       (criteria 7, 9)
    """
    if request.method == 'GET':
        date_param = request.GET.get('date')
        qs = Booking.objects.all()
        if date_param:
            qs = qs.filter(reservation_date=date_param)
        data = [
            {
                'id': b.id,
                'first_name': b.first_name,
                'reservation_date': b.reservation_date.isoformat(),
                'reservation_slot': b.reservation_slot.strftime('%H:%M'),
            }
            for b in qs
        ]
        return JsonResponse(data, safe=False)

    # POST
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        payload = request.POST

    first_name = payload.get('first_name', '').strip()
    reservation_date = payload.get('reservation_date')
    reservation_slot = payload.get('reservation_slot')

    if not (first_name and reservation_date and reservation_slot):
        return JsonResponse({'error': 'first_name, reservation_date and reservation_slot are required.'}, status=400)

    if Booking.objects.filter(reservation_date=reservation_date, reservation_slot=reservation_slot).exists():
        return JsonResponse({'error': 'That time slot is already booked for the selected date.'}, status=409)

    booking = Booking.objects.create(
        first_name=first_name,
        reservation_date=reservation_date,
        reservation_slot=reservation_slot,
    )
    return JsonResponse({
        'id': booking.id,
        'first_name': booking.first_name,
        'reservation_date': reservation_date,
        'reservation_slot': reservation_slot,
    }, status=201)
