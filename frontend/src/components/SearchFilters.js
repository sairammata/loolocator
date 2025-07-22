import React from 'react';
import { Settings, Accessibility } from 'lucide-react';

const SearchFilters = ({ searchRadius, accessibilityOnly, onFiltersChange }) => {
  const handleRadiusChange = (e) => {
    const newRadius = parseInt(e.target.value);
    onFiltersChange(newRadius, accessibilityOnly);
  };

  const handleAccessibilityToggle = (e) => {
    const newAccessibility = e.target.checked;
    onFiltersChange(searchRadius, newAccessibility);
  };

  const radiusOptions = [
    { value: 500, label: '0.5 km' },
    { value: 1000, label: '1 km' },
    { value: 2000, label: '2 km' },
    { value: 5000, label: '5 km' },
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center mb-4">
        <Settings className="h-5 w-5 text-gray-600 mr-2" />
        <h3 className="text-lg font-medium text-gray-900">Search Filters</h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Search Radius */}
        <div>
          <label htmlFor="radius" className="block text-sm font-medium text-gray-700 mb-2">
            Search Radius
          </label>
          <select
            id="radius"
            value={searchRadius}
            onChange={handleRadiusChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            {radiusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Accessibility Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Accessibility
          </label>
          <div className="flex items-center">
            <input
              type="checkbox"
              id="accessibility"
              checked={accessibilityOnly}
              onChange={handleAccessibilityToggle}
              className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <label
              htmlFor="accessibility"
              className="ml-3 flex items-center text-sm text-gray-700 cursor-pointer"
            >
              <Accessibility className="h-4 w-4 mr-1 text-green-600" />
              Wheelchair accessible only
            </label>
          </div>
        </div>
      </div>
      
      {/* Active Filters Summary */}
      <div className="mt-4 flex flex-wrap gap-2">
        <span className="inline-flex items-center bg-primary-100 text-primary-800 text-xs font-medium px-2 py-1 rounded-full">
          Radius: {radiusOptions.find(option => option.value === searchRadius)?.label}
        </span>
        {accessibilityOnly && (
          <span className="inline-flex items-center bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full">
            <Accessibility className="h-3 w-3 mr-1" />
            Accessible Only
          </span>
        )}
      </div>
    </div>
  );
};

export default SearchFilters;