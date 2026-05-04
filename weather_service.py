import requests


def get_weather(city):
    api_key = "83da0a8aee21fc895d87a038591d49af"
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
        response = requests.get(url, timeout=5)
        print(f"DEBUG: Weather Status Code: {response.status_code}")
        print(f"DEBUG: Response Body: {response.text}")  # И эту

        if response.status_code == 200:
            data = response.json()
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description']
            return f"В городе {city.capitalize()} сейчас {desc}, температура {temp}°C."
        elif response.status_code == 404:
            return f"Город '{city}' не найден. Проверь название!"
        else:
            return "Сервис погоды временно недоступен."
    except Exception as e:
        print(f"Weather error: {e}")
        return "Произошла ошибка при запросе погоды."