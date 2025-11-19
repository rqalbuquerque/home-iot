from datetime import date
from dataclasses import dataclass

@dataclass
class EnergyConsumption:
	"""
	Represents the energy consumption of a device on a specific date.
	"""
	device_id: str
	used_date: date
	energy_wh: float

	def __post_init__(self):
		if not self.device_id:
			raise ValueError("device_id must not be empty")
		if not isinstance(self.energy_wh, (int, float)) or self.energy_wh < 0:
			raise ValueError("energy_wh must be a non-negative number")
