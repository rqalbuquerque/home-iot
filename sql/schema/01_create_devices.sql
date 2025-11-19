CREATE TABLE IF NOT EXISTS devices (
    id VARCHAR(65) PRIMARY KEY,
    device_type VARCHAR(50),
    model_name VARCHAR(100),
    alias VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
