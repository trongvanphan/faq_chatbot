"""
Car Database Module
Contains comprehensive car specifications and data for the recommendation agent.
"""

class CarDatabase:
    """
    Comprehensive car database with detailed specifications for recommendation matching.
    """
    
    def __init__(self):
        self.cars = {
            "Toyota Camry": {
                "price_range": "$25,000-$35,000",
                "fuel_economy": "Excellent (28-38 mpg)",
                "size": "Mid-size sedan (5 passengers)",
                "purposes": ["daily_commute", "family", "business"],
                "priorities": ["fuel_economy", "reliability", "smooth_ride"],
                "brand_origin": "Japanese",
                "safety_rating": "5-star",
                "technology": "Standard infotainment, Apple CarPlay",
                "style": "Conservative, elegant",
                "drivetrain": "FWD",
                "body_type": "sedan"
            },
            "Honda CR-V": {
                "price_range": "$28,000-$38,000",
                "fuel_economy": "Very Good (27-32 mpg)",
                "size": "Compact SUV (5 passengers, large cargo)",
                "purposes": ["family", "daily_commute", "leisure"],
                "priorities": ["cargo_space", "reliability", "safety"],
                "brand_origin": "Japanese",
                "safety_rating": "5-star",
                "technology": "Honda Sensing, large touchscreen",
                "style": "Practical, family-friendly",
                "drivetrain": "AWD available",
                "body_type": "compact_suv"
            },
            "Hyundai Elantra": {
                "price_range": "$20,000-$28,000",
                "fuel_economy": "Excellent (31-41 mpg)",
                "size": "Compact sedan (5 passengers)",
                "purposes": ["daily_commute", "budget_friendly"],
                "priorities": ["fuel_economy", "technology", "warranty"],
                "brand_origin": "Korean",
                "safety_rating": "5-star",
                "technology": "Large touchscreen, wireless charging",
                "style": "Youthful, modern",
                "drivetrain": "FWD",
                "body_type": "sedan"
            },
            "BMW 3 Series": {
                "price_range": "$35,000-$55,000",
                "fuel_economy": "Good (23-30 mpg)",
                "size": "Luxury sedan (5 passengers)",
                "purposes": ["business", "luxury", "performance"],
                "priorities": ["driving_feel", "luxury", "technology"],
                "brand_origin": "German",
                "safety_rating": "5-star",
                "technology": "Premium iDrive system, premium audio",
                "style": "Sporty, elegant, luxurious",
                "drivetrain": "RWD/AWD",
                "body_type": "sedan"
            },
            "Ford F-150": {
                "price_range": "$32,000-$70,000",
                "fuel_economy": "Fair (20-24 mpg)",
                "size": "Full-size pickup (6 passengers, large cargo)",
                "purposes": ["work", "towing", "family"],
                "priorities": ["cargo_space", "towing", "durability"],
                "brand_origin": "American",
                "safety_rating": "5-star",
                "technology": "SYNC 4, large touchscreen",
                "style": "Rugged, powerful",
                "drivetrain": "4WD available",
                "body_type": "pickup"
            },
            "Tesla Model 3": {
                "price_range": "$38,000-$55,000",
                "fuel_economy": "Excellent (Electric - 120+ MPGe)",
                "size": "Mid-size sedan (5 passengers)",
                "purposes": ["daily_commute", "tech_enthusiast", "eco_friendly"],
                "priorities": ["technology", "fuel_economy", "performance"],
                "brand_origin": "American (Electric)",
                "safety_rating": "5-star",
                "technology": "Autopilot, large touchscreen, OTA updates",
                "style": "Modern, minimalist, futuristic",
                "drivetrain": "RWD/AWD",
                "body_type": "sedan"
            },
            "Mazda CX-5": {
                "price_range": "$27,000-$37,000",
                "fuel_economy": "Good (25-31 mpg)",
                "size": "Compact SUV (5 passengers, good cargo)",
                "purposes": ["family", "leisure", "daily_commute"],
                "priorities": ["driving_feel", "style", "quality"],
                "brand_origin": "Japanese",
                "safety_rating": "5-star",
                "technology": "Mazda Connect, Bose audio available",
                "style": "Elegant, sporty, sophisticated",
                "drivetrain": "AWD available",
                "body_type": "compact_suv"
            },
            # Additional cars to expand the database
            "Subaru Outback": {
                "price_range": "$29,000-$40,000",
                "fuel_economy": "Good (26-33 mpg)",
                "size": "Mid-size wagon/SUV (5 passengers, large cargo)",
                "purposes": ["family", "outdoor_adventure", "daily_commute", "all_weather"],
                "priorities": ["reliability", "safety", "cargo_space", "all_weather"],
                "brand_origin": "Japanese",
                "safety_rating": "5-star",
                "technology": "EyeSight, Starlink system",
                "style": "Rugged, practical, outdoorsy",
                "drivetrain": "Standard AWD",
                "body_type": "wagon"
            },
            "Kia Telluride": {
                "price_range": "$35,000-$50,000",
                "fuel_economy": "Fair (20-26 mpg)",
                "size": "Large SUV (8 passengers, massive cargo)",
                "purposes": ["large_family", "towing", "road_trips"],
                "priorities": ["passenger_space", "cargo_space", "comfort", "value"],
                "brand_origin": "Korean",
                "safety_rating": "5-star",
                "technology": "Large touchscreen, premium audio available",
                "style": "Bold, premium, family-focused",
                "drivetrain": "AWD available",
                "body_type": "large_suv"
            }
        }
    
    def get_all_cars(self):
        """Return all cars in the database."""
        return self.cars
    
    def get_cars_by_budget(self, max_budget):
        """Filter cars by maximum budget."""
        filtered_cars = {}
        for car_name, specs in self.cars.items():
            price_range = specs["price_range"]
            # Extract maximum price from range (e.g., "$25,000-$35,000" -> 35000)
            max_price = int(price_range.split('-')[1].replace('$', '').replace(',', ''))
            if max_price <= max_budget:
                filtered_cars[car_name] = specs
        return filtered_cars
    
    def get_cars_by_purpose(self, purposes):
        """Filter cars by purposes."""
        if isinstance(purposes, str):
            purposes = [purposes]
        
        filtered_cars = {}
        for car_name, specs in self.cars.items():
            car_purposes = specs["purposes"]
            if any(purpose in car_purposes for purpose in purposes):
                filtered_cars[car_name] = specs
        return filtered_cars
    
    def get_cars_by_brand_origin(self, brand_origin):
        """Filter cars by brand origin."""
        filtered_cars = {}
        for car_name, specs in self.cars.items():
            if specs["brand_origin"].lower() == brand_origin.lower():
                filtered_cars[car_name] = specs
        return filtered_cars
    
    def get_cars_by_body_type(self, body_type):
        """Filter cars by body type."""
        filtered_cars = {}
        for car_name, specs in self.cars.items():
            if specs.get("body_type", "").lower() == body_type.lower():
                filtered_cars[car_name] = specs
        return filtered_cars

# Data validation constants
VALID_FUEL_ECONOMY_LEVELS = [
    "Poor (15-19 mpg)", "Fair (20-24 mpg)", "Good (25-31 mpg)",
    "Very Good (32-36 mpg)", "Excellent (37+ mpg)",
    "Excellent Hybrid (40-50 mpg)", "Outstanding Hybrid (50+ mpg)",
    "Electric (100-110 MPGe)", "Electric (110-120 MPGe)", "Electric (120+ MPGe)"
]

VALID_PURPOSES = [
    "daily_commute", "city_driving", "highway_cruising", "short_trips",
    "family", "school_runs", "family_road_trips", "child_transport",
    "business", "work_commute", "client_meetings", "professional_image",
    "leisure", "weekend_trips", "camping_outdoors", "road_trips",
    "towing", "hauling_cargo", "work", "construction_work",
    "luxury", "performance_driving", "tech_enthusiast", "eco_friendly",
    "budget_friendly", "outdoor_adventure", "all_weather", "large_family"
]

VALID_PRIORITIES = [
    "fuel_economy", "low_maintenance", "reliability", "durability", "resale_value",
    "driving_feel", "acceleration", "handling", "power", "sportiness",
    "smooth_ride", "quiet_cabin", "comfortable_seats", "spacious_interior",
    "cargo_space", "passenger_space", "storage_solutions", "versatility",
    "technology", "infotainment", "connectivity", "driver_assistance",
    "safety", "crash_protection", "driver_aids", "visibility",
    "style", "design", "luxury", "prestige", "uniqueness",
    "affordability", "warranty", "dealer_network", "towing", "all_weather"
]

VALID_BRAND_ORIGINS = [
    "Japanese", "Korean", "Chinese", "German", "Italian", "French",
    "British", "Swedish", "American", "American (Electric)"
]

VALID_SAFETY_RATINGS = [
    "5-star", "4-star", "3-star", "5-star NHTSA", "4-star NHTSA",
    "Top Safety Pick+ IIHS", "Top Safety Pick IIHS", "Excellent safety"
]

VALID_STYLES = [
    "Conservative, elegant", "Traditional, refined", "Modern, minimalist, futuristic",
    "Youthful, modern", "Sporty, elegant, luxurious", "Elegant, sporty, sophisticated",
    "Rugged, powerful", "Practical, family-friendly", "Bold, premium, family-focused",
    "Rugged, practical, outdoorsy"
]
