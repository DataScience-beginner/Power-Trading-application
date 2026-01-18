import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Autocomplete,
  Grid,
  Paper,
  Typography,
  Chip,
  CircularProgress
} from '@mui/material';
import { LocationOn } from '@mui/icons-material';

interface Location {
  name: string;
  state: string;
  lat: number;
  lon: number;
  region: string;
}

// Pre-populated major renewable energy hubs in India
const PRESET_LOCATIONS: Location[] = [
  // Tamil Nadu
  { name: 'Chennai', state: 'Tamil Nadu', lat: 13.0827, lon: 80.2707, region: 'Tamil Nadu Solar Belt' },
  { name: 'Coimbatore', state: 'Tamil Nadu', lat: 11.0168, lon: 76.9558, region: 'Tamil Nadu Solar Belt' },
  { name: 'Madurai', state: 'Tamil Nadu', lat: 9.9252, lon: 78.1198, region: 'Tamil Nadu Solar Belt' },
  { name: 'Tiruchirappalli', state: 'Tamil Nadu', lat: 10.7905, lon: 78.7047, region: 'Tamil Nadu Solar Belt' },
  
  // Karnataka
  { name: 'Bangalore', state: 'Karnataka', lat: 12.9716, lon: 77.5946, region: 'Karnataka Solar Cluster' },
  { name: 'Mysore', state: 'Karnataka', lat: 12.2958, lon: 76.6394, region: 'Karnataka Solar Cluster' },
  { name: 'Belgaum', state: 'Karnataka', lat: 15.8497, lon: 74.4977, region: 'Karnataka Solar Cluster' },
  
  // Gujarat
  { name: 'Ahmedabad', state: 'Gujarat', lat: 23.0225, lon: 72.5714, region: 'Gujarat Wind Corridor' },
  { name: 'Surat', state: 'Gujarat', lat: 21.1702, lon: 72.8311, region: 'Gujarat Wind Corridor' },
  { name: 'Kutch', state: 'Gujarat', lat: 23.7337, lon: 69.8597, region: 'Gujarat Wind Corridor' },
  
  // Rajasthan
  { name: 'Jaipur', state: 'Rajasthan', lat: 26.9124, lon: 75.7873, region: 'Rajasthan Solar Parks' },
  { name: 'Jodhpur', state: 'Rajasthan', lat: 26.2389, lon: 73.0243, region: 'Rajasthan Solar Parks' },
  { name: 'Bikaner', state: 'Rajasthan', lat: 28.0229, lon: 73.3119, region: 'Rajasthan Solar Parks' },
  
  // Maharashtra
  { name: 'Mumbai', state: 'Maharashtra', lat: 19.0760, lon: 72.8777, region: 'Maharashtra Wind Belt' },
  { name: 'Pune', state: 'Maharashtra', lat: 18.5204, lon: 73.8567, region: 'Maharashtra Wind Belt' },
  { name: 'Satara', state: 'Maharashtra', lat: 17.6805, lon: 73.9903, region: 'Maharashtra Wind Belt' },
  
  // Andhra Pradesh & Telangana
  { name: 'Hyderabad', state: 'Telangana', lat: 17.3850, lon: 78.4867, region: 'Telangana Solar Belt' },
  { name: 'Visakhapatnam', state: 'Andhra Pradesh', lat: 17.6868, lon: 83.2185, region: 'Andhra Pradesh Solar Belt' },
  { name: 'Anantapur', state: 'Andhra Pradesh', lat: 14.6819, lon: 77.6006, region: 'Andhra Pradesh Solar Belt' },
];

// Group locations by region
const REGIONS = [...new Set(PRESET_LOCATIONS.map(loc => loc.region))];

interface LocationPickerProps {
  onLocationSelect: (lat: number, lon: number, name?: string) => void;
  currentLat?: number;
  currentLon?: number;
}

export default function LocationPicker({ onLocationSelect, currentLat, currentLon }: LocationPickerProps) {
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [geocodeResults, setGeocodeResults] = useState<Location[]>([]);
  const [loading, setLoading] = useState(false);

  // Debounced geocoding search
  useEffect(() => {
    if (searchQuery.length < 3) {
      setGeocodeResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        // Use Open-Meteo Geocoding API
        const response = await fetch(
          `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(searchQuery)}&count=10&language=en&format=json`
        );
        const data = await response.json();
        
        if (data.results) {
          const results: Location[] = data.results.map((r: any) => ({
            name: r.name,
            state: r.admin1 || r.country,
            lat: r.latitude,
            lon: r.longitude,
            region: 'Search Result'
          }));
          setGeocodeResults(results);
        }
      } catch (error) {
        console.error('Geocoding error:', error);
      } finally {
        setLoading(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleLocationSelect = (location: Location | null) => {
    if (location) {
      setSelectedLocation(location);
      onLocationSelect(location.lat, location.lon, location.name);
    }
  };

  const allLocations = [...PRESET_LOCATIONS, ...geocodeResults];

  return (
    <Box>
      <Autocomplete
        options={allLocations}
        groupBy={(option) => option.region}
        getOptionLabel={(option) => `${option.name}, ${option.state}`}
        value={selectedLocation}
        onChange={(_, newValue) => handleLocationSelect(newValue)}
        inputValue={searchQuery}
        onInputChange={(_, newValue) => setSearchQuery(newValue)}
        loading={loading}
        renderInput={(params) => (
          <TextField
            {...params}
            label="Search Location"
            placeholder="Type city name or select from presets..."
            InputProps={{
              ...params.InputProps,
              startAdornment: <LocationOn color="action" sx={{ mr: 1 }} />,
              endAdornment: (
                <>
                  {loading ? <CircularProgress size={20} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
          />
        )}
        renderOption={(props, option) => (
          <li {...props}>
            <Box>
              <Typography variant="body2">
                <strong>{option.name}</strong>, {option.state}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {option.lat.toFixed(4)}°N, {option.lon.toFixed(4)}°E
              </Typography>
            </Box>
          </li>
        )}
      />

      {/* Region Quick Select Chips */}
      <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        <Typography variant="caption" color="text.secondary" sx={{ width: '100%', mb: 0.5 }}>
          Quick Select by Region:
        </Typography>
        {REGIONS.map(region => (
          <Chip
            key={region}
            label={region}
            size="small"
            onClick={() => {
              const firstLocation = PRESET_LOCATIONS.find(loc => loc.region === region);
              if (firstLocation) handleLocationSelect(firstLocation);
            }}
            color="primary"
            variant="outlined"
          />
        ))}
      </Box>

      {/* Current coordinates display */}
      {currentLat && currentLon && (
        <Paper sx={{ mt: 2, p: 1, bgcolor: 'grey.50' }}>
          <Typography variant="caption" color="text.secondary">
            Selected: <strong>{currentLat.toFixed(4)}°N, {currentLon.toFixed(4)}°E</strong>
            {selectedLocation && ` (${selectedLocation.name})`}
          </Typography>
        </Paper>
      )}
    </Box>
  );
}
