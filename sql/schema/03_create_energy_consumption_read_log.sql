CREATE TABLE IF NOT EXISTS energy_consumption_read_log (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(65) REFERENCES devices(id),
    start_date DATE NOT NULL,
    end_date DATE,
    read_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (device_id)
);
