import pywhatkit
import datetime

from assistant_features import (
    get_location,
    get_current_weather,
    WEATHER_INTERPRETATION_CODES,
)

ASSISTANT_NAME = 'гарик'


def is_command_about_time(command: str) -> bool:
    return (
            ("который час" in command)
            or ("время" in command)
            or ("времени" in command)
    )


def is_command_about_playing(command: str) -> bool:
    return "включи" in command


def is_command_about_weather(command: str) -> bool:
    return (
            ("погода" in command)
            or ("погоды" in command)
            or ("погоде" in command)
            or ("погоду" in command)
            or ("погодой" in command)
    )


def analyze_text(text: str):
    if ASSISTANT_NAME not in text:
        return

    command = text.replace(ASSISTANT_NAME, "")
    print("Command:", command)

    if is_command_about_time(command):
        time = datetime.datetime.now().strftime("%H:%M")
        print(f"Сейчас {time}")
    elif is_command_about_playing(command):
        topic = command.replace("включи", "").strip()
        pywhatkit.playonyt(topic)
        print(f"включаю {topic}")
    elif is_command_about_weather(command):
        location = get_location()
        weather = get_current_weather(location)
        print(f"Сейчас {weather.get('temperature')} градуса. "
              f"Скорость ветра - {weather.get('windspeed')} километров в час. "
              + WEATHER_INTERPRETATION_CODES.get(weather.get('weathercode'))
              )
