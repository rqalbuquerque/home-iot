CREATE TABLE IF NOT EXISTS energy_consumption (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(65) REFERENCES devices(id),
    used_date DATE NOT NULL,
    energy_wh DECIMAL(12,3) NOT NULL,  -- consumo em Watt-hour
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (device_id, used_date)
);
