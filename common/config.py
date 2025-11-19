import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

def _validate_env_vars(required_vars):
	missing = [var for var in required_vars if os.getenv(var) is None]
	if missing:
		raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

@dataclass
class LgApiConfig:
	"""
	LG ThinQ API configuration loaded from environment variables.
	"""
	LG_COUNTRY: str = os.getenv("LG_COUNTRY")
	LG_API_KEY: str = os.getenv("LG_API_KEY")
	LG_API_TOKEN: str = os.getenv("LG_API_TOKEN")
	LG_CLIENT_ID: str = os.getenv("LG_CLIENT_ID")

_validate_env_vars(["LG_COUNTRY", "LG_API_KEY", "LG_API_TOKEN", "LG_CLIENT_ID"])

@dataclass
class PostgresConfig:
	"""
	PostgreSQL connection configuration loaded from environment variables.
	"""
	POSTGRES_USER: str = os.getenv("POSTGRES_USER")
	POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
	POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
	POSTGRES_DB: str = os.getenv("POSTGRES_DB")
	POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

_validate_env_vars(["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_DB"])

@dataclass
class RabbitMQConfig:
	"""
	RabbitMQ connection configuration loaded from environment variables.
	"""
	RABBITMQ_HOST: str = os.getenv("RABBITMQ_HOST", "rabbitmq")
	RABBITMQ_QUEUE: str = os.getenv("RABBITMQ_QUEUE", "rabbitmq_queue")

_validate_env_vars(["RABBITMQ_HOST", "RABBITMQ_QUEUE"])