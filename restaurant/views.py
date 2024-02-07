# from django.http import HttpResponse
from django.shortcuts import render,redirect
from .forms import BookingForm
from .models import Menu
from django.core import serializers
from .models import Booking
from datetime import datetime
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse


# Create your views here.
def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def reservations(request):
    date = request.GET.get('date',datetime.today().date())
    bookings = Booking.objects.all()
    booking_json = serializers.serialize('json', bookings)
    return render(request, 'bookings.html',{"bookings":booking_json})

def book(request):
    form = BookingForm()
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request, 'book.html', context)

def menu(request):
    menu_data = Menu.objects.all()
    main_data = {"menu": menu_data}
    return render(request, 'menu.html', {"menu": main_data})


def display_menu_item(request, pk=None): 
    if pk: 
        menu_item = Menu.objects.get(pk=pk) 
    else: 
        menu_item = "" 
    return render(request, 'menu_item.html', {"menu_item": menu_item}) 

from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
import json

@require_http_methods(["POST", "GET"])  # Ensure this view accepts only POST and GET requests
def bookings(request):
    if request.method == 'POST':
        # Load the JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))  # Correct decoding of the request body
        
        # Check for existing booking for the given date and slot
        exist = Booking.objects.filter(reservation_date=data['reservation_date'], reservation_slot=data['reservation_slot']).exists()
        
        if exist:
            # If the slot is already booked, return an error message
            return JsonResponse({'error': 'This slot is already booked. Please choose another.'}, status=409)  # 409 Conflict
        else:
            # If the slot is free, proceed to create a new booking
            try:
                booking = Booking(
                    first_name=data['first_name'],
                    reservation_date=data['reservation_date'],
                    reservation_slot=data['reservation_slot'],
                )
                booking.full_clean()  # Validates the model instance
                booking.save()
                return JsonResponse({'success': 'Your booking has been successfully saved.'})
            except ValidationError as e:
                # If the booking data is invalid, return an error message
                return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'GET':
        date = request.GET.get('date', datetime.today().date())
        bookings = Booking.objects.filter(reservation_date=date)
        booking_json = serializers.serialize('json', bookings)
        return HttpResponse(booking_json, content_type='application/json')
