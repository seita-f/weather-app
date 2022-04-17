from django.shortcuts import render
from django.http import HttpResponse
import requests
import math # for math.ceil and math.floor
import datetime
from decouple import config # env

# API
key = config('KEY')

"""
/*******************************
        Function
*******************************/
"""
# Function for rounding temperature
def round_Temp(positive, temp):

    number_dec = str(temp - int(temp))[1:]  # take out decimal
    if(positive):
        if (float(number_dec) < 0.5):  # round down
            return math.floor(temp)
        else:  # round up
            return math.ceil(temp)
    else:
        if (float(number_dec) < 0.5):  # round down
            temp *= -1  # make it positive
            temp = math.floor(temp)
            temp *= -1
            return math.floor(temp)
        else:  # round up
            temp *= -1  # make it positive
            temp = math.floor(temp)
            temp *= -1
            return math.ceil(temp)

def get_date(timezone):
    tz = datetime.timezone(datetime.timedelta(seconds=int(timezone)))
    return datetime.datetime.now(tz = tz).strftime("%H:%M") # %m/%d/%Y => Month/Day/Year
    #strftime is just for visually formatting the datetime object

"""
/*******************************
        Return Page
*******************************/
"""
def main(request):
    city = "Warsaw"  # default
    # send request twice for the following things
    ### daily info ###
    url_daily = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=' + key
    city_weather = requests.get(url_daily.format(city)).json()  # request the API data and convert the JSON to Python data types

    ### hourly info ###
    API_Key = key

    url = 'http://api.openweathermap.org/data/2.5/forecast'
    query = {
        'units': 'metric',
        'q': city,
        'cnt': '10',
        'appid': API_Key
    }
    try:
        r = requests.get(url, params=query)
    except:
        print("Request Error")

    ### daily info ###
    # Convert temp from F ro C
    min_C = (city_weather['main']['temp_min']-32)*5/9
    max_C = (city_weather['main']['temp_max']-32)*5/9
    feels_C = (city_weather['main']['feels_like']-32)*5/9

    # Round temp
    if(min_C > 0):
        min_C = round_Temp(True, min_C)
    else:
        min_C = round_Temp(False, min_C)

    if(max_C > 0):
        max_C = round_Temp(True, max_C)
    else:
        max_C = round_Temp(False, max_C)

    if(feels_C > 0):
        feels_C = round_Temp(True, feels_C)
    else:
        feels_C = round_Temp(False, feels_C)

    weather = {
        'city': city,
        'min_temp': min_C,
        'max_temp': max_C,
        'description': city_weather['weather'][0]['description'],
        'icon': city_weather['weather'][0]['icon'],
        'feels_like': feels_C,
        'pressure': city_weather['main']['pressure'],
        'humidity': city_weather['main']['humidity'],
        'wind_speed': round_Temp(True, city_weather['wind']['speed']), # this function can be used to wind_speed too
        'timezone': get_date(city_weather['timezone']),
    }

    ### hourly info ###
    date_time = []
    temp_hour = []
    weather_hour = []
    icon_hour = []

    for x in range(r.json()['cnt']):

        time_str = r.json()['list'][x]['dt_txt']
        sliced1 = time_str[10:]  # remove year and date
        size = len(sliced1)
        sliced2 = sliced1[:size-3] # remove minutes => :00
        date_time.append(sliced2)

        temp_hour_round = r.json()['list'][x]['main']['temp']
        # Rounding
        if (temp_hour_round > 0):
            temp_hour.append(round_Temp(True, temp_hour_round))
        else:
            temp_hour.append(round_Temp(False, temp_hour_round))

        weather_hour.append(r.json()['list'][x]['weather'][0]['main'])
        icon_hour.append(r.json()['list'][x]['weather'][0]['icon'])

    # Test
    if len(date_time) != 10 or len(temp_hour) != 10 or len(weather_hour) != 10 or len(icon_hour) != 10:
        return print("Array doesn't have 10 elements")
    # combine
    weather_details = zip(date_time, temp_hour, weather_hour, icon_hour)

    return render(request, 'first_app/main.html', {"weather_details": weather_details, 'weather': weather})


def forecast(request):

    # send request twice for the following things
    ### hourly info ###
    API_Key = key
    city = "Warsaw"  # default

    if request.POST['city']:  # name = 'city' in html
        city = request.POST['city']

    url = 'http://api.openweathermap.org/data/2.5/forecast'
    query = {
        'units': 'metric',
        'q': city,
        'cnt': '10',
        'appid': API_Key
    }

    try:
        r = requests.get(url, params=query)
    except:
        print("Request get error!!!")

    ### daily info ###
    url_daily = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=' + key
    city_weather = requests.get(url_daily.format(city)).json()  # request the API data and convert the JSON to Python data types

    # when city is not found
    if(city_weather["cod"] == "404"):
        message = "Not Found"
        return render(request, 'first_app/forecast.html', {"message": message})

    # Convert temp from F ro C
    min_C = (city_weather['main']['temp_min'] - 32) * 5 / 9
    max_C = (city_weather['main']['temp_max'] - 32) * 5 / 9
    feels_C = (city_weather['main']['feels_like'] - 32) * 5 / 9

    # Round temp
    if (min_C > 0):
        min_C = round_Temp(True, min_C)
    else:
        min_C = round_Temp(False, min_C)

    if (max_C > 0):
        max_C = round_Temp(True, max_C)
    else:
        max_C = round_Temp(False, max_C)

    if (feels_C > 0):
        feels_C = round_Temp(True, feels_C)
    else:
        feels_C = round_Temp(False, feels_C)

    weather = {
            'city': city,
            'min_temp': min_C,
            'max_temp': max_C,
            'description': city_weather['weather'][0]['description'],
            'icon': city_weather['weather'][0]['icon'],
            'feels_like': feels_C,
            'pressure': city_weather['main']['pressure'],
            'humidity': city_weather['main']['humidity'],
            'wind_speed': round_Temp(True, city_weather['wind']['speed']),  # this function can be used to wind_speed too
            'timezone': get_date(city_weather['timezone']),
        }

    ### hourly info ###
    date_time = []
    temp_hour = []
    weather_hour = []
    icon_hour = []

    for x in range(r.json()['cnt']):

        time_str = r.json()['list'][x]['dt_txt']
        sliced1 = time_str[10:] # remove year and date
        size = len(sliced1)
        sliced2 = sliced1[:size - 3]  # remove minutes => :00
        date_time.append(sliced2)

        temp_hour_round = r.json()['list'][x]['main']['temp']
        # Rounding
        if(temp_hour_round > 0):
            temp_hour.append(round_Temp(True, temp_hour_round))
        else:
            temp_hour.append(round_Temp(False, temp_hour_round))

        weather_hour.append(r.json()['list'][x]['weather'][0]['main'])
        icon_hour.append(r.json()['list'][x]['weather'][0]['icon'])

    # Test
    if len(date_time) != 10 or len(temp_hour) != 10 or len(weather_hour) != 10 or len(icon_hour) != 10:
        return print("Array doesn't have 10 elements")

    # weather_detail = {'date_time': date_time, 'temp_hour': temp_hour, 'weather_hour': weather_hour}
    weather_details = zip(date_time, temp_hour, weather_hour, icon_hour)

    return render(request, 'first_app/forecast.html', {"weather_details": weather_details, 'weather': weather})