from dataclasses import dataclass

@dataclass
class Device:
	"""
	Represents a device registered in the LG ThinQ database.
	"""
	id: str
	device_type: str
	model_name: str
	alias: str
