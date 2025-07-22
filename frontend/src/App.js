import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapPin, Search, Star, Navigation, Clock, Shield, Accessibility } from 'lucide-react';
import MapComponent from './components/MapComponent';
import WashroomCard from './components/WashroomCard';
import LocationButton from './components/LocationButton';
import SearchFilters from './components/SearchFilters';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [washrooms, setWashrooms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userLocation, setUserLocation] = useState(null);
  const [selectedWashroom, setSelectedWashroom] = useState(null);
  const [error, setError] = useState('');
  const [searchRadius, setSearchRadius] = useState(1000);
  const [accessibilityOnly, setAccessibilityOnly] = useState(false);

  // Get user's current location
  const getCurrentLocation = () => {
    setLoading(true);
    setError('');
    
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        };
        setUserLocation(location);
        findNearestWashrooms(location);
      },
      (error) => {
        let errorMessage = 'Unable to get your location';
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location access denied. Please enable location services.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information unavailable.';
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out.';
            break;
          default:
            errorMessage = 'An unknown error occurred while getting location.';
            break;
        }
        setError(errorMessage);
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutes
      }
    );
  };

  // Find nearest washrooms
  const findNearestWashrooms = async (location = userLocation) => {
    if (!location) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/washrooms/nearest`, {
        params: {
          latitude: location.latitude,
          longitude: location.longitude,
          radius: searchRadius,
          limit: 20,
          accessibility_required: accessibilityOnly
        }
      });
      
      setWashrooms(response.data);
    } catch (error) {
      console.error('Error finding washrooms:', error);
      setError('Failed to find nearby washrooms. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Search with updated filters
  const handleFiltersChange = (radius, accessibility) => {
    setSearchRadius(radius);
    setAccessibilityOnly(accessibility);
    // The useEffect will automatically trigger when these state values change
  };

  // Load initial data with demo location (NYC)
  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      try {
        // Use NYC as default location for demo
        const demoLocation = { latitude: 40.7589, longitude: -73.9851 };
        setUserLocation(demoLocation);
        await findNearestWashrooms(demoLocation);
      } catch (error) {
        console.error('Error loading initial data:', error);
        setError('Failed to load washroom data');
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, [searchRadius, accessibilityOnly]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <MapPin className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">LooLocator</h1>
                <p className="text-sm text-gray-500">Find nearest washrooms</p>
              </div>
            </div>
            <LocationButton onClick={getCurrentLocation} loading={loading} />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <div className="text-red-600 mr-3">⚠️</div>
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Search Filters */}
        <div className="mb-8">
          <SearchFilters
            searchRadius={searchRadius}
            accessibilityOnly={accessibilityOnly}
            onFiltersChange={handleFiltersChange}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Map Section */}
          <div className="order-2 lg:order-1">
            <div className="card h-full">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <Navigation className="h-5 w-5 mr-2 text-primary-600" />
                Map View
              </h2>
              
              {userLocation ? (
                <MapComponent
                  userLocation={userLocation}
                  washrooms={washrooms}
                  selectedWashroom={selectedWashroom}
                  onWashroomSelect={setSelectedWashroom}
                />
              ) : (
                <div className="map-container bg-gray-100 flex items-center justify-center">
                  <p className="text-gray-500">Enable location to see map</p>
                </div>
              )}
            </div>
          </div>

          {/* Washrooms List Section */}
          <div className="order-1 lg:order-2">
            <div className="card h-full">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                  <Search className="h-5 w-5 mr-2 text-primary-600" />
                  Nearby Washrooms
                </h2>
                {washrooms.length > 0 && (
                  <span className="bg-primary-100 text-primary-800 text-sm font-medium px-3 py-1 rounded-full">
                    {washrooms.length} found
                  </span>
                )}
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="spinner"></div>
                  <p className="ml-3 text-gray-600">Finding washrooms...</p>
                </div>
              ) : washrooms.length > 0 ? (
                <div className="washroom-list max-h-96 overflow-y-auto space-y-4">
                  {washrooms.map((washroom) => (
                    <WashroomCard
                      key={washroom.id}
                      washroom={washroom}
                      isSelected={selectedWashroom?.id === washroom.id}
                      onClick={() => setSelectedWashroom(washroom)}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 text-lg">No washrooms found nearby</p>
                  <p className="text-gray-400 text-sm mt-2">
                    Try increasing the search radius or enable location services
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 text-center shadow-sm border border-gray-100">
            <Shield className="h-8 w-8 text-green-600 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Verified Locations</h3>
            <p className="text-gray-600 text-sm mt-1">All washrooms are verified and regularly updated</p>
          </div>
          
          <div className="bg-white rounded-xl p-6 text-center shadow-sm border border-gray-100">
            <Accessibility className="h-8 w-8 text-blue-600 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Accessibility Info</h3>
            <p className="text-gray-600 text-sm mt-1">Detailed accessibility information for every location</p>
          </div>
          
          <div className="bg-white rounded-xl p-6 text-center shadow-sm border border-gray-100">
            <Clock className="h-8 w-8 text-purple-600 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-gray-900">Real-time Updates</h3>
            <p className="text-gray-600 text-sm mt-1">Live information about hours and availability</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;