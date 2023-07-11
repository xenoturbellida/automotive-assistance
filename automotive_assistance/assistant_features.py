import requests


GET_LOCATION_URL = 'http://ip-api.com/json/'
GET_WEATHER_URL = 'https://api.open-meteo.com/v1/forecast'

WEATHER_INTERPRETATION_CODES = {
    0: "Чистое небо",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Сплошная облачность",
    45: "Туман",
    48: "Ледяной туман",
    51: "Лёгкая морось",
    53: "Умеренная морось",
    55: "Густая морось",
    56: "Лёгкая ледяная морось",
    57: "Густая ледяная морось",
    61: "Лёгкий дождь",
    63: "Умеренный дождь",
    65: "Ливень",
    66: "Лёгкий ледяной дождь",
    67: "Ледяной ливень",
    71: "Лёгкий снег",
    73: "Снег",
    75: "Снегопад",
    77: "Град",
    80: "Лёгкие ливневые дожди",
    81: "Умеренные ливневые дожди",
    82: "Сильные ливневые дожди",
    85: "Лёгкий снежный дождь",
    86: "Сильный снежный дождь",
    95: "Гроза",
    96: "Гроза с лёгким градом",
    99: "Гроза с сильным градом",
}


def get_location() -> dict:
    response = requests.get(f"{GET_LOCATION_URL}?fields=status,message,lat,lon,timezone")
    if response.status_code == 200:
        data = response.json()
        return {
            'latitude': data.get('lat'),
            'longitude': data.get('lon'),
            'timezone': data.get('timezone'),
        }


def get_current_weather(location: {str: str}) -> dict:
    query = (
        GET_WEATHER_URL +
        f"?latitude={location['latitude']}"
        f"&longitude={location['longitude']}"
        "&current_weather=true"
        f"&timezone={location['timezone']}"
        "&forecast_days=1"
    )
    response = requests.get(query)
    if response.status_code == 200:
        current_weather = response.json().get('current_weather')
        return current_weather
