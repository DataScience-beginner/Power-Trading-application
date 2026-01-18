-- Migration: Add AI forecasting fields to clients table
-- Date: 2026-01-18
-- Description: Add lat, lon, capacity_kw, farm_type for power forecasting

-- Add columns (PostgreSQL syntax)
ALTER TABLE clients 
ADD COLUMN IF NOT EXISTS lat FLOAT DEFAULT 12.97,
ADD COLUMN IF NOT EXISTS lon FLOAT DEFAULT 80.22,
ADD COLUMN IF NOT EXISTS capacity_kw INTEGER DEFAULT 5000,
ADD COLUMN IF NOT EXISTS farm_type VARCHAR DEFAULT 'solar';

-- Update existing clients to have default Chennai coordinates
UPDATE clients 
SET lat = 12.97, lon = 80.22, capacity_kw = 5000, farm_type = 'solar'
WHERE lat IS NULL OR lon IS NULL;

-- Add comments
COMMENT ON COLUMN clients.lat IS 'Latitude for weather forecasting';
COMMENT ON COLUMN clients.lon IS 'Longitude for weather forecasting';
COMMENT ON COLUMN clients.capacity_kw IS 'Solar/wind farm capacity in kW';
COMMENT ON COLUMN clients.farm_type IS 'Farm type: solar or wind';
