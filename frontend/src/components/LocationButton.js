import React from 'react';
import { Navigation, Loader } from 'lucide-react';

const LocationButton = ({ onClick, loading }) => {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className={`
        flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200
        ${loading 
          ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
          : 'bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2'
        }
      `}
    >
      {loading ? (
        <>
          <Loader className="h-4 w-4 animate-spin" />
          <span>Finding location...</span>
        </>
      ) : (
        <>
          <Navigation className="h-4 w-4" />
          <span>Use My Location</span>
        </>
      )}
    </button>
  );
};

export default LocationButton;