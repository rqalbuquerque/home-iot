import psycopg2

class PostgresConn:
	"""Context manager for managing PostgreSQL connections."""
	def __init__(self, conn_string: str):
		self.conn_string = conn_string
		self.conn = None

	def __enter__(self):
		self.conn = psycopg2.connect(self.conn_string)
		return self.conn

	def __exit__(self, exc_type, exc_value, traceback):
		if self.conn:
			if exc_type:
				self.conn.rollback()
			else:
				self.conn.commit()
			self.conn.close()
