import React from 'react';
import { MapPin, Star, Clock, Accessibility, Shield } from 'lucide-react';

const WashroomCard = ({ washroom, isSelected, onClick }) => {
  const formatDistance = (distance) => {
    if (!distance) return '';
    if (distance < 1000) {
      return `${Math.round(distance)}m`;
    }
    return `${(distance / 1000).toFixed(1)}km`;
  };

  const getAmenityIcon = (amenity) => {
    const amenityMap = {
      'wheelchair_accessible': '♿',
      'baby_changing': '👶',
      'hand_sanitizer': '🧴',
      'air_conditioning': '❄️',
      'outdoor_access': '🚪',
      'water_fountain': '🚰'
    };
    return amenityMap[amenity] || '✓';
  };

  const getAmenityLabel = (amenity) => {
    const labelMap = {
      'wheelchair_accessible': 'Wheelchair Accessible',
      'baby_changing': 'Baby Changing Station',
      'hand_sanitizer': 'Hand Sanitizer',
      'air_conditioning': 'Air Conditioning',
      'outdoor_access': 'Outdoor Access',
      'water_fountain': 'Water Fountain'
    };
    return labelMap[amenity] || amenity.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div
      onClick={onClick}
      className={`
        p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 hover:shadow-md
        ${isSelected 
          ? 'border-primary-500 bg-primary-50 shadow-md' 
          : 'border-gray-200 bg-white hover:border-gray-300'
        }
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <h3 className="font-semibold text-gray-900 text-lg">{washroom.name}</h3>
            {washroom.verified && (
              <Shield className="h-4 w-4 text-green-500" title="Verified Location" />
            )}
          </div>
          <div className="flex items-center text-gray-600 text-sm">
            <MapPin className="h-4 w-4 mr-1" />
            <span className="flex-1">{washroom.address}</span>
          </div>
        </div>
        {washroom.distance && (
          <div className="bg-primary-100 text-primary-800 text-sm font-medium px-2 py-1 rounded-full ml-3">
            {formatDistance(washroom.distance)}
          </div>
        )}
      </div>

      {/* Rating and Hours */}
      <div className="flex items-center space-x-4 mb-3">
        <div className="flex items-center">
          <Star className="h-4 w-4 text-yellow-500 mr-1" fill="currentColor" />
          <span className="text-gray-700 font-medium">{washroom.rating}</span>
          <span className="text-gray-500 text-sm ml-1">/5</span>
        </div>
        <div className="flex items-center text-gray-600 text-sm">
          <Clock className="h-4 w-4 mr-1" />
          <span>{washroom.hours}</span>
        </div>
        {washroom.accessibility && (
          <div className="flex items-center text-green-600 text-sm">
            <Accessibility className="h-4 w-4 mr-1" />
            <span>Accessible</span>
          </div>
        )}
      </div>

      {/* Description */}
      {washroom.description && (
        <p className="text-gray-600 text-sm mb-3">{washroom.description}</p>
      )}

      {/* Amenities */}
      {washroom.amenities && washroom.amenities.length > 0 && (
        <div className="space-y-1">
          <p className="text-gray-700 text-sm font-medium">Amenities:</p>
          <div className="flex flex-wrap gap-2">
            {washroom.amenities.map((amenity, index) => (
              <div
                key={index}
                className="flex items-center bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full"
                title={getAmenityLabel(amenity)}
              >
                <span className="mr-1">{getAmenityIcon(amenity)}</span>
                <span>{getAmenityLabel(amenity)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Click indicator */}
      <div className={`mt-3 text-xs ${isSelected ? 'text-primary-600' : 'text-gray-400'}`}>
        {isSelected ? '📍 Selected on map' : 'Click to view on map'}
      </div>
    </div>
  );
};

export default WashroomCard;