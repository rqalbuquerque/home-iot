from psycopg2.extras import RealDictCursor
from typing import List, Optional
from common.postgres_connection import PostgresConn
from common.device import Device

class DeviceDAL:
	"""
	Data Access Layer for LG ThinQ devices.
	Responsible for read operations on the devices table.
	"""
	def __init__(self, conn):
		self.conn = conn

	def get(self, device_id: str) -> Optional[Device]:
		sql = "SELECT * FROM devices WHERE id = %s;"
		try:
			with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
				cur.execute(sql, (device_id,))
				row = cur.fetchone()
		except Exception as e:
			print(f"Error fetching device: {e}")
			return None
		if not row:
			return None
		return Device(
			id=row["id"],
			device_type=row["device_type"],
			model_name=row["model_name"],
			alias=row["alias"]
		)

	def insert(self, device: Device):
		sql = """
			INSERT INTO devices (id, device_type, model_name, alias)
			VALUES (%s, %s, %s, %s)
			ON CONFLICT (id) DO NOTHING;
		"""
		params = (device.id, device.device_type, device.model_name, device.alias)
		try:
			with self.conn.cursor() as cur:
				cur.execute(sql, params)
		except Exception as e:
			print(f"Error inserting device: {e}")

	def bulk_insert(self, devices: List[Device]):
		sql = """
			INSERT INTO devices (id, device_type, model_name, alias)
			VALUES (%s, %s, %s, %s)
			ON CONFLICT (id) DO NOTHING;
		"""
		params = [
			(device.id, device.device_type, device.model_name, device.alias)
			for device in devices
		]
		try:
			with self.conn.cursor() as cur:
				cur.executemany(sql, params)
		except Exception as e:
			print(f"Error bulk inserting devices: {e}")

	def list(self) -> List[Device]:
		sql = "SELECT * FROM devices;"
		try:
			with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
				cur.execute(sql)
				rows = cur.fetchall()
		except Exception as e:
			print(f"Error listing devices: {e}")
			return []
		return [
			Device(
				id=row["id"],
				device_type=row["device_type"],
				model_name=row["model_name"],
				alias=row["alias"]
			)
			for row in rows
		]
