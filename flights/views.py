# flights/views.py
import requests
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

API_KEY = os.environ.get("AMADEUS_API_KEY")
API_SECRET = os.environ.get("AMADEUS_API_SECRET")



def get_amadeus_access_token():
    endpoint = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = f'grant_type=client_credentials&client_id={API_KEY}&client_secret={API_SECRET}'
    try:
        response = requests.post(endpoint, headers=headers, data=payload)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"Amadeus Token Error: {e}")
        return None


@login_required
def flight_search_view(request):
    context = {}
    if 'fly_from' in request.GET and request.GET.get('fly_from'):
        fly_from_iata = request.GET.get('fly_from')
        fly_to_iata = request.GET.get('fly_to')
        date_from_str = request.GET.get('date_from')

        context['search_params'] = request.GET

        access_token = get_amadeus_access_token()
        if not access_token:
            context['error'] = "Could not authenticate with flight provider."
            return render(request, 'flights/flight_search.html', context)

        endpoint = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'originLocationCode': fly_from_iata.upper(),
            'destinationLocationCode': fly_to_iata.upper(),
            'departureDate': date_from_str,
            'adults': 1,
            'max': 10
        }

        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            api_data = response.json()

            flights = []
            carriers_dict = api_data.get('dictionaries', {}).get('carriers', {})

            for offer in api_data.get('data', []):
                try:
                    itinerary = offer['itineraries'][0]
                    segment = itinerary['segments'][0]

                    # Aviakompaniya nomini lug'atdan topamiz
                    carrier_code = segment.get('carrierCode')
                    airline_name = carriers_dict.get(carrier_code, "Unknown Airline")

                    flights.append({
                        'price': offer['price']['total'],
                        'departure_time': segment['departure']['at'],
                        'arrival_time': segment['arrival']['at'],
                        'duration': itinerary['duration'].replace('PT', '').replace('H', 'h ').replace('M', 'm'),
                        'airlines': [airline_name],  # Endi to'liq nomni qo'shamiz
                        'deep_link': f"https://www.google.com/flights?q={fly_from_iata} to {fly_to_iata} on {date_from_str}",
                    })
                except (KeyError, IndexError) as e:

                    print(f"Skipping an offer due to parsing error: {e}")
                    continue

            context['flights'] = flights
            if not flights:
                context['no_results'] = "No flights found for this route on the selected date."
        except Exception as e:
            context['error'] = f"An error occurred: {e}"

    return render(request, 'flights/flight_search.html', context)