from typing import List
from datetime import datetime
from common.postgres_connection import PostgresConn
from common.energy_consumption import EnergyConsumption

class EnergyConsumptionDAL:
	def __init__(self, conn):
		self.conn = conn

	def get_log(self, device_id: str):
		sql = "SELECT start_date, end_date FROM energy_consumption_read_log WHERE device_id = %s"
		with self.conn.cursor() as cur:
			cur.execute(sql, (device_id,))
			return cur.fetchone()

	def create_log(self, device_id: str, start_date):
		sql = """
		INSERT INTO energy_consumption_read_log (device_id, start_date, end_date)
		VALUES (%s, %s, %s)
		ON CONFLICT (device_id) DO NOTHING;
		"""
		with self.conn.cursor() as cur:
			cur.execute(sql, (device_id, start_date, None))

	def update_log(self, device_id: str, end_date):
		sql = "UPDATE energy_consumption_read_log SET end_date = %s, read_timestamp = NOW() WHERE device_id = %s"
		with self.conn.cursor() as cur:
			cur.execute(sql, (end_date, device_id))

	def log_read(self, device_id: str, start_date, end_date):
		sql = """
			INSERT INTO energy_consumption_read_log (device_id, start_date, end_date)
			VALUES (%s, %s, %s);
		"""
		params = (device_id, start_date, end_date)
		with self.conn.cursor() as cur:
			cur.execute(sql, params)

	def insert(self, usage: EnergyConsumption):
		sql = """
			INSERT INTO energy_consumption (device_id, used_date, energy_wh)
			VALUES (%s, %s, %s)
			ON CONFLICT DO NOTHING;
		"""
		params = (
			usage.device_id,
			usage.used_date,
			usage.energy_wh
		)
		with self.conn.cursor() as cur:
			cur.execute(sql, params)

	def bulk_insert(self, rows: List[EnergyConsumption]):
		sql = """
			INSERT INTO energy_consumption (device_id, used_date, energy_wh)
			VALUES (%s, %s, %s)
			ON CONFLICT DO NOTHING;
		"""
		data = [
			(
				row.device_id,
				row.used_date,
				row.energy_wh
			)
			for row in rows
		]
		with self.conn.cursor() as cur:
			cur.executemany(sql, data)
