import requests
import json
from googletrans import Translator
from dotenv import load_dotenv
import os

load_dotenv()
api_token = os.getenv("X-RapidAPI-Key")


def property_hotel(id_hotel):
    url = "https://hotels4.p.rapidapi.com/properties/v2/get-summary"

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "ru_RU",
        "siteId": 300000001,
        "propertyId": id_hotel
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": api_token,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    file_read = json.loads(response.text)

    name = f"{file_read['data']['propertyInfo']['summary']['name']}\n"

    description = file_read['data']['propertyInfo']['summary']['tagline']
    translator = Translator()
    result = translator.translate(description, dest='ru')
    result_description = f"{result.text}\n"

    address = f"{file_read['data']['propertyInfo']['summary']['location']['address']['addressLine']}\n"
    images = list()
    for image in file_read['data']['propertyInfo']['propertyGallery']['images']:
        images.append(image['image']['url'])

    descr = [name, result_description, address, images]

    return descr
