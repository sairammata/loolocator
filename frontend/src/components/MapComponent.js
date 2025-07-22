import React, { useEffect, useRef, useState } from 'react';
import { Loader } from '@googlemaps/js-api-loader';

const MapComponent = ({ userLocation, washrooms, selectedWashroom, onWashroomSelect }) => {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const markersRef = useRef([]);
  const userMarkerRef = useRef(null);
  const [mapError, setMapError] = useState('');
  const [isMapLoaded, setIsMapLoaded] = useState(false);

  // Initialize Google Maps
  useEffect(() => {
    const initMap = async () => {
      try {
        // Try to get API key from backend
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/maps/api-key`);
        
        if (!response.ok) {
          setMapError('Google Maps API key not configured. Map functionality unavailable.');
          return;
        }
        
        const { api_key } = await response.json();
        
        const loader = new Loader({
          apiKey: api_key,
          version: 'weekly',
          libraries: ['places', 'geometry']
        });

        await loader.load();
        
        // Initialize map
        const map = new window.google.maps.Map(mapRef.current, {
          center: userLocation || { lat: 40.7589, lng: -73.9851 },
          zoom: 14,
          styles: [
            {
              featureType: 'poi',
              elementType: 'labels',
              stylers: [{ visibility: 'off' }]
            }
          ],
          mapTypeControl: false,
          streetViewControl: false,
          fullscreenControl: false
        });

        mapInstance.current = map;
        setIsMapLoaded(true);

      } catch (error) {
        console.error('Error loading Google Maps:', error);
        setMapError('Failed to load Google Maps. Please check your internet connection.');
      }
    };

    if (mapRef.current) {
      initMap();
    }
  }, [userLocation]);

  // Update user location marker
  useEffect(() => {
    if (!mapInstance.current || !userLocation || !isMapLoaded) return;

    // Remove existing user marker
    if (userMarkerRef.current) {
      userMarkerRef.current.setMap(null);
    }

    // Add user location marker
    const userMarker = new window.google.maps.Marker({
      position: { lat: userLocation.latitude, lng: userLocation.longitude },
      map: mapInstance.current,
      title: 'Your Location',
      icon: {
        path: window.google.maps.SymbolPath.CIRCLE,
        scale: 8,
        fillColor: '#4285F4',
        fillOpacity: 1,
        strokeColor: '#ffffff',
        strokeWeight: 2
      }
    });

    userMarkerRef.current = userMarker;

    // Center map on user location
    mapInstance.current.setCenter({ lat: userLocation.latitude, lng: userLocation.longitude });
  }, [userLocation, isMapLoaded]);

  // Update washroom markers
  useEffect(() => {
    if (!mapInstance.current || !isMapLoaded) return;

    // Clear existing markers
    markersRef.current.forEach(marker => marker.setMap(null));
    markersRef.current = [];

    // Add washroom markers
    washrooms.forEach((washroom) => {
      const marker = new window.google.maps.Marker({
        position: { 
          lat: washroom.location.latitude, 
          lng: washroom.location.longitude 
        },
        map: mapInstance.current,
        title: washroom.name,
        icon: {
          url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
            <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="16" r="15" fill="#0ea5e9" stroke="white" stroke-width="2"/>
              <path d="M10 12h12v8H10z" fill="white"/>
              <circle cx="16" cy="10" r="2" fill="white"/>
            </svg>
          `),
          scaledSize: new window.google.maps.Size(32, 32)
        }
      });

      // Info window for marker
      const infoWindow = new window.google.maps.InfoWindow({
        content: `
          <div style="padding: 8px; max-width: 250px;">
            <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600;">${washroom.name}</h3>
            <p style="margin: 0 0 4px 0; font-size: 14px; color: #666;">${washroom.address}</p>
            <div style="display: flex; align-items: center; margin: 4px 0;">
              <span style="color: #0ea5e9; font-size: 14px;">★ ${washroom.rating}</span>
              <span style="margin-left: 12px; font-size: 14px; color: #666;">
                ${washroom.distance ? `${washroom.distance}m away` : ''}
              </span>
            </div>
            <p style="margin: 8px 0 0 0; font-size: 12px; color: #888;">${washroom.hours}</p>
          </div>
        `
      });

      // Click handler for marker
      marker.addListener('click', () => {
        infoWindow.open(mapInstance.current, marker);
        onWashroomSelect(washroom);
      });

      markersRef.current.push(marker);
    });
  }, [washrooms, onWashroomSelect, isMapLoaded]);

  // Highlight selected washroom
  useEffect(() => {
    if (!mapInstance.current || !selectedWashroom || !isMapLoaded) return;

    const selectedMarker = markersRef.current.find((marker, index) => 
      washrooms[index]?.id === selectedWashroom.id
    );

    if (selectedMarker) {
      // Center map on selected washroom
      mapInstance.current.setCenter(selectedMarker.getPosition());
      
      // Trigger click to show info window
      window.google.maps.event.trigger(selectedMarker, 'click');
    }
  }, [selectedWashroom, washrooms, isMapLoaded]);

  if (mapError) {
    return (
      <div className="map-container bg-red-50 border border-red-200 flex flex-col items-center justify-center text-center p-6">
        <div className="text-red-600 text-4xl mb-4">🗺️</div>
        <p className="text-red-800 font-medium mb-2">Map Unavailable</p>
        <p className="text-red-600 text-sm">{mapError}</p>
        <div className="mt-4 text-xs text-red-500">
          <p>To enable maps:</p>
          <p>1. Get a Google Maps API key</p>
          <p>2. Add it to the backend .env file</p>
          <p>3. Restart the backend service</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      <div ref={mapRef} className="map-container bg-gray-100">
        {!isMapLoaded && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
            <div className="spinner"></div>
            <span className="ml-3 text-gray-600">Loading map...</span>
          </div>
        )}
      </div>
      
      {isMapLoaded && (
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg px-3 py-2 text-sm">
          <div className="flex items-center text-gray-600">
            <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
            Your Location
          </div>
          <div className="flex items-center text-gray-600 mt-1">
            <div className="w-3 h-3 bg-primary-600 rounded-full mr-2"></div>
            Washrooms
          </div>
        </div>
      )}
    </div>
  );
};

export default MapComponent;