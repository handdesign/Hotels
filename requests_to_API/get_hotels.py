import requests
import json
from requests_to_API.cur import currency_converter
from dotenv import load_dotenv
import os

load_dotenv()
api_token = os.getenv("X-RapidAPI-Key")
currency_now = currency_converter()


def input_data(
		city_request: str,
		date_in: dict,
		date_out: dict,
		quantity: int,
		sort_property: str,
		max_price=999999,
		min_price=1
		):

	url = "https://hotels4.p.rapidapi.com/properties/v2/list"

	payload = {
		"currency": "USD",
		"eapid": 1,
		"locale": "ru_RU",
		"siteId": 300000001,
		"destination": {"regionId": city_request},
		"checkInDate": date_in,
		"checkOutDate": date_out,
		"rooms": [
			{
				"adults": 2
			}
		],
		"resultsStartingIndex": 0,
		"resultsSize": quantity,
		"sort": sort_property,
		"filters": {"price": {
			"max": max_price,
			"min": min_price
		}}
	}
	headers = {
		"content-type": "application/json",
		"X-RapidAPI-Key": api_token,
		"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
	}

	response = requests.request("POST", url, json=payload, headers=headers)

	file_read = json.loads(response.text)

	id_sites = dict()
	for item in file_read['data']['propertySearch']['properties']:
		id_site = item['id']
		get_price = round(item["price"]["lead"]["amount"] / currency_now)
		price = f'Цена за одну ночь в отеле {get_price} рублей\n'
		destination_info = item['destinationInfo']['distanceFromDestination']['value']
		destination = f'Расстояние до центра города {destination_info}км\n'
		id_sites[id_site] = [get_price, price, destination]

	return id_sites
