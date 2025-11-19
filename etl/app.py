import logging
from datetime import date, timedelta
from common.config import LgApiConfig, PostgresConfig
from common.device_dal import DeviceDAL
from common.lg_api_client import LGApiClient
from common.energy_consumption_dal import EnergyConsumptionDAL
from common.postgres_connection import PostgresConn
from common.date_range_splitter import DateRangeSplitter

postgres_config = PostgresConfig()
postgres_conn_string = f"postgresql://{postgres_config.POSTGRES_USER}:{postgres_config.POSTGRES_PASSWORD}@{postgres_config.POSTGRES_HOST}:5432/{postgres_config.POSTGRES_DB}"

lg_api_config = LgApiConfig()
api_client = LGApiClient(
    lg_api_config.LG_COUNTRY,
    lg_api_config.LG_API_KEY,
    lg_api_config.LG_CLIENT_ID,
    lg_api_config.LG_API_TOKEN
)

def run(device_id: str):            
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logger = logging.getLogger(__name__)

    yesterday = date.today() - timedelta(days=1)
    default_start = date(2025, 1, 1)

    with PostgresConn(postgres_conn_string) as conn:
        device_dal = DeviceDAL(conn)
        device = device_dal.get(device_id)
        if not device:
            logger.error(f"Device with ID {device_id} not found.")
            return
        
        energy_consumption_dal = EnergyConsumptionDAL(conn)
        log = energy_consumption_dal.get_log(device.id)
        if not log:
            energy_consumption_dal.create_log(device.id, default_start)
            start_date = default_start
            end_date = yesterday
        else:
            start_date, last_end_date = log
            if last_end_date:
                start_date = last_end_date + timedelta(days=1)
            else:
                start_date = default_start
            end_date = yesterday
        if start_date > end_date:
            logger.warning(f"Device {device.id}: No new data to fetch.")
            return
        
        splitter = DateRangeSplitter(max_count_records=30)
        ranges = splitter.split(start_date, end_date)
        for r_start, r_end in ranges:
            logger.info(f"Device {device.id}: Fetching {r_start} to {r_end} from LG API")
            consumption = api_client.get_energy_consumption(device.id, r_start, r_end)
            try:
                energy_consumption_dal.bulk_insert(consumption)
                energy_consumption_dal.update_log(device.id, r_end)
                logger.info(f"Device {device.id}: Updated log to {r_end}")
            except Exception as e:
                logger.error(f"Device {device.id}: Error saving data or updating log: {e}")
                break