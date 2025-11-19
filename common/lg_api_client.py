from common.device import Device
from common.energy_consumption import EnergyConsumption
import requests
import uuid
from datetime import datetime, date
from enum import Enum

class LGApiResponseCode(Enum):
	NORMAL_RESPONSE = "0000"
	NOT_OWNED_DEVICE = "1212"
	NOT_SUPPORTED_PRODUCT = "1221"
	NOT_SUPPORTED_PROPERTY = "1220"
	NOT_SUPPORTED_COUNTRY = "1307"
	FAIL_REQUEST = "2214"

class LGApiClient:
	def __init__(self, country, api_key, client_id, token):
		self.base_url = "https://api-aic.lgthinq.com"
		self.headers = {
			"x-message-id": str(uuid.uuid4()),
			"x-country": country,
			"x-api-key": api_key,
			"x-client-id": client_id,
			"Authorization": "Bearer {}".format(token),
		}

	def get_devices(self):
		url = f"{self.base_url}/devices"
		response = requests.get(url, headers=self.headers)
		response.raise_for_status()
		return [self.to_device(d) for d in response.json()["response"]]

	def to_device(self, device):
		return Device(
			id=device["deviceId"],
			device_type=device["deviceInfo"]["deviceType"],
			model_name=device["deviceInfo"]["modelName"],
			alias=device["deviceInfo"]["alias"]
		)

	def get_energy_consumption(self, device_id, start_date: date, end_date: date):
		if (end_date - start_date).days < 0 or (end_date - start_date).days > 30:
			raise Exception(f"Invalid date range: {start_date} - {end_date}")
		params = {
			"period": "DAILY",
			"startDate": start_date.strftime("%Y%m%d"),
			"endDate": end_date.strftime("%Y%m%d")
		}
		url = f"{self.base_url}/devices/energy/{device_id}/usage"
		response = requests.get(url, params=params, headers=self.headers)
		response.raise_for_status()
		response_data = response.json()
		if response_data["response"]["resultCode"] == LGApiResponseCode.NORMAL_RESPONSE.value:
			return [self.to_energy_consumption(device_id, consumption) for consumption in response_data["response"]["result"]["dataList"]]
		else:
			result_code = LGApiResponseCode(response_data["response"]["resultCode"])
			raise Exception(f"Unexpected Result Code '{result_code}' from LG API.")

	def to_energy_consumption(self, device_id, consumption):
		return EnergyConsumption(
			device_id=device_id,
			used_date=datetime.strptime(consumption["usedDate"], "%Y%m%d").strftime("%Y-%m-%d"),
			energy_wh=float(consumption["energyUsage"])
		)
