from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, GEOSPHERE
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
from geopy.distance import geodesic
import asyncio
from datetime import datetime
import uuid

load_dotenv()

app = FastAPI(title="LooLocator API", description="Find nearest washrooms/restrooms")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "loolocator_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]
washrooms_collection = db.washrooms

# Pydantic models
class Location(BaseModel):
    latitude: float
    longitude: float

class Washroom(BaseModel):
    id: Optional[str] = None
    name: str
    location: Location
    address: str
    description: Optional[str] = ""
    amenities: List[str] = []
    accessibility: bool = False
    rating: float = 0.0
    hours: Optional[str] = "24/7"
    verified: bool = False
    created_at: Optional[datetime] = None

class WashroomResponse(Washroom):
    distance: Optional[float] = None

class ReviewModel(BaseModel):
    washroom_id: str
    rating: int
    comment: Optional[str] = ""
    user_name: Optional[str] = "Anonymous"
    created_at: Optional[datetime] = None

# Initialize database and create indexes
@app.on_event("startup")
async def startup_db():
    """Initialize database with geospatial index and seed data"""
    
    # Create geospatial index
    try:
        await washrooms_collection.create_index([("location", GEOSPHERE)])
        print("Geospatial index created successfully")
    except Exception as e:
        print(f"Index creation error (may already exist): {e}")
    
    # Check if collection is empty and seed data
    count = await washrooms_collection.count_documents({})
    if count == 0:
        await seed_washroom_data()

async def seed_washroom_data():
    """Seed database with sample washroom data"""
    sample_washrooms = [
        {
            "id": str(uuid.uuid4()),
            "name": "Central Park Restroom",
            "location": {"type": "Point", "coordinates": [-73.968285, 40.785091]},
            "address": "Central Park, New York, NY 10024",
            "description": "Clean public restroom in Central Park",
            "amenities": ["wheelchair_accessible", "baby_changing", "hand_sanitizer"],
            "accessibility": True,
            "rating": 4.2,
            "hours": "6:00 AM - 12:00 AM",
            "verified": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Times Square Public Restroom",
            "location": {"type": "Point", "coordinates": [-73.985130, 40.758896]},
            "address": "Times Square, New York, NY 10036",
            "description": "Public restroom facility in Times Square area",
            "amenities": ["wheelchair_accessible", "air_conditioning"],
            "accessibility": True,
            "rating": 3.8,
            "hours": "24/7",
            "verified": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Brooklyn Bridge Park Restroom",
            "location": {"type": "Point", "coordinates": [-73.996900, 40.700292]},
            "address": "Brooklyn Bridge Park, Brooklyn, NY 11201",
            "description": "Modern restroom facility with great East River views",
            "amenities": ["wheelchair_accessible", "baby_changing", "outdoor_access"],
            "accessibility": True,
            "rating": 4.5,
            "hours": "5:00 AM - 11:00 PM",
            "verified": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Washington Square Park Restroom",
            "location": {"type": "Point", "coordinates": [-73.997332, 40.730823]},
            "address": "Washington Square Park, New York, NY 10012",
            "description": "Public restroom in Greenwich Village",
            "amenities": ["wheelchair_accessible"],
            "accessibility": True,
            "rating": 3.5,
            "hours": "6:00 AM - 10:00 PM",
            "verified": True,
            "created_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "name": "High Line Park Restroom",
            "location": {"type": "Point", "coordinates": [-74.004862, 40.748441]},
            "address": "High Line Park, New York, NY 10011",
            "description": "Modern restroom facility on the High Line",
            "amenities": ["wheelchair_accessible", "baby_changing", "water_fountain"],
            "accessibility": True,
            "rating": 4.1,
            "hours": "7:00 AM - 7:00 PM",
            "verified": True,
            "created_at": datetime.utcnow()
        }
    ]
    
    await washrooms_collection.insert_many(sample_washrooms)
    print(f"Seeded {len(sample_washrooms)} washroom records")

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "LooLocator API"}

@app.get("/api/washrooms/nearest", response_model=List[WashroomResponse])
async def get_nearest_washrooms(
    latitude: float = Query(..., description="User's latitude"),
    longitude: float = Query(..., description="User's longitude"),
    radius: int = Query(1000, description="Search radius in meters"),
    limit: int = Query(10, description="Maximum number of results"),
    accessibility_required: bool = Query(False, description="Filter for accessible washrooms only")
):
    """Find nearest washrooms based on user location"""
    
    try:
        # Build aggregation pipeline for geospatial query
        pipeline = [
            {
                "$geoNear": {
                    "near": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "distanceField": "distance",
                    "maxDistance": radius,
                    "spherical": True
                }
            }
        ]
        
        # Add accessibility filter if required
        if accessibility_required:
            pipeline.append({"$match": {"accessibility": True}})
        
        # Limit results
        pipeline.append({"$limit": limit})
        
        # Execute query
        cursor = washrooms_collection.aggregate(pipeline)
        washrooms = await cursor.to_list(length=limit)
        
        # Format response
        response_data = []
        for washroom in washrooms:
            # Convert GeoJSON coordinates back to lat/lng for frontend
            coordinates = washroom["location"]["coordinates"]
            washroom_data = {
                "id": washroom["id"],
                "name": washroom["name"],
                "location": {
                    "latitude": coordinates[1],  # GeoJSON is [lng, lat]
                    "longitude": coordinates[0]
                },
                "address": washroom["address"],
                "description": washroom["description"],
                "amenities": washroom["amenities"],
                "accessibility": washroom["accessibility"],
                "rating": washroom["rating"],
                "hours": washroom["hours"],
                "verified": washroom["verified"],
                "created_at": washroom["created_at"],
                "distance": round(washroom["distance"], 2)
            }
            response_data.append(WashroomResponse(**washroom_data))
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding washrooms: {str(e)}")

@app.get("/api/washrooms", response_model=List[Washroom])
async def get_all_washrooms(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(50, description="Maximum number of results")
):
    """Get all washrooms with pagination"""
    
    try:
        cursor = washrooms_collection.find().skip(skip).limit(limit)
        washrooms = await cursor.to_list(length=limit)
        
        response_data = []
        for washroom in washrooms:
            # Convert GeoJSON coordinates back to lat/lng for frontend
            coordinates = washroom["location"]["coordinates"]
            washroom_data = {
                "id": washroom["id"],
                "name": washroom["name"],
                "location": {
                    "latitude": coordinates[1],  # GeoJSON is [lng, lat]
                    "longitude": coordinates[0]
                },
                "address": washroom["address"],
                "description": washroom["description"],
                "amenities": washroom["amenities"],
                "accessibility": washroom["accessibility"],
                "rating": washroom["rating"],
                "hours": washroom["hours"],
                "verified": washroom["verified"],
                "created_at": washroom["created_at"]
            }
            response_data.append(Washroom(**washroom_data))
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching washrooms: {str(e)}")

@app.post("/api/washrooms", response_model=Washroom)
async def add_washroom(washroom: Washroom):
    """Add a new washroom"""
    
    try:
        washroom_data = washroom.dict()
        washroom_data["id"] = str(uuid.uuid4())
        washroom_data["created_at"] = datetime.utcnow()
        
        result = await washrooms_collection.insert_one(washroom_data)
        
        if result.inserted_id:
            return Washroom(**washroom_data)
        else:
            raise HTTPException(status_code=500, detail="Failed to create washroom")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating washroom: {str(e)}")

@app.get("/api/washrooms/{washroom_id}", response_model=Washroom)
async def get_washroom(washroom_id: str):
    """Get specific washroom by ID"""
    
    try:
        washroom = await washrooms_collection.find_one({"id": washroom_id})
        
        if not washroom:
            raise HTTPException(status_code=404, detail="Washroom not found")
        
        # Convert GeoJSON coordinates back to lat/lng for frontend
        coordinates = washroom["location"]["coordinates"]
        washroom_data = {
            "id": washroom["id"],
            "name": washroom["name"],
            "location": {
                "latitude": coordinates[1],  # GeoJSON is [lng, lat]
                "longitude": coordinates[0]
            },
            "address": washroom["address"],
            "description": washroom["description"],
            "amenities": washroom["amenities"],
            "accessibility": washroom["accessibility"],
            "rating": washroom["rating"],
            "hours": washroom["hours"],
            "verified": washroom["verified"],
            "created_at": washroom["created_at"]
        }
        
        return Washroom(**washroom_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching washroom: {str(e)}")

@app.get("/api/maps/api-key")
async def get_maps_api_key():
    """Get Google Maps API key for frontend"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key or api_key == "your_google_maps_api_key_here":
        raise HTTPException(status_code=500, detail="Google Maps API key not configured")
    return {"api_key": api_key}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)