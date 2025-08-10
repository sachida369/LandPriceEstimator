import logging
from models import User, City, Locality, InfrastructureMultiplier, APIKey
from app import db
from config import Config
import secrets

def seed_initial_data():
    """Seed initial data if database is empty"""
    try:
        # Check if data already exists
        if City.query.first():
            return
        
        logging.info("Seeding initial data...")
        
        # Create admin user
        admin_user = User.query.filter_by(username=Config.ADMIN_USERNAME).first()
        if not admin_user:
            admin_user = User(
                username=Config.ADMIN_USERNAME,
                email=Config.ADMIN_EMAIL,
                is_admin=True
            )
            admin_user.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin_user)
        
        # Seed cities with real Indian data
        cities_data = [
            # Tier 1 cities
            {'name': 'Mumbai', 'state': 'Maharashtra', 'price': 25000, 'growth': 0.08, 'population': 12442373, 'tier': 'Tier 1'},
            {'name': 'Delhi', 'state': 'Delhi', 'price': 22000, 'growth': 0.07, 'population': 11007835, 'tier': 'Tier 1'},
            {'name': 'Bangalore', 'state': 'Karnataka', 'price': 18000, 'growth': 0.09, 'population': 8443675, 'tier': 'Tier 1'},
            {'name': 'Hyderabad', 'state': 'Telangana', 'price': 15000, 'growth': 0.08, 'population': 6993262, 'tier': 'Tier 1'},
            {'name': 'Chennai', 'state': 'Tamil Nadu', 'price': 14000, 'growth': 0.06, 'population': 4681087, 'tier': 'Tier 1'},
            {'name': 'Kolkata', 'state': 'West Bengal', 'price': 12000, 'growth': 0.05, 'population': 4496694, 'tier': 'Tier 1'},
            {'name': 'Pune', 'state': 'Maharashtra', 'price': 16000, 'growth': 0.08, 'population': 3124458, 'tier': 'Tier 1'},
            {'name': 'Ahmedabad', 'state': 'Gujarat', 'price': 8500, 'growth': 0.07, 'population': 5633927, 'tier': 'Tier 1'},
            
            # Tier 2 cities
            {'name': 'Jaipur', 'state': 'Rajasthan', 'price': 6500, 'growth': 0.06, 'population': 3073350, 'tier': 'Tier 2'},
            {'name': 'Lucknow', 'state': 'Uttar Pradesh', 'price': 5500, 'growth': 0.06, 'population': 2817105, 'tier': 'Tier 2'},
            {'name': 'Kanpur', 'state': 'Uttar Pradesh', 'price': 4500, 'growth': 0.05, 'population': 2767031, 'tier': 'Tier 2'},
            {'name': 'Nagpur', 'state': 'Maharashtra', 'price': 5500, 'growth': 0.06, 'population': 2405421, 'tier': 'Tier 2'},
            {'name': 'Indore', 'state': 'Madhya Pradesh', 'price': 5000, 'growth': 0.06, 'population': 1964086, 'tier': 'Tier 2'},
            {'name': 'Thane', 'state': 'Maharashtra', 'price': 18000, 'growth': 0.07, 'population': 1818872, 'tier': 'Tier 2'},
            {'name': 'Bhopal', 'state': 'Madhya Pradesh', 'price': 4500, 'growth': 0.05, 'population': 1798218, 'tier': 'Tier 2'},
            {'name': 'Visakhapatnam', 'state': 'Andhra Pradesh', 'price': 6000, 'growth': 0.06, 'population': 1730320, 'tier': 'Tier 2'},
            {'name': 'Pimpri-Chinchwad', 'state': 'Maharashtra', 'price': 12000, 'growth': 0.07, 'population': 1729359, 'tier': 'Tier 2'},
            {'name': 'Patna', 'state': 'Bihar', 'price': 4000, 'growth': 0.05, 'population': 1684222, 'tier': 'Tier 2'},
            {'name': 'Vadodara', 'state': 'Gujarat', 'price': 6500, 'growth': 0.06, 'population': 1666703, 'tier': 'Tier 2'},
            {'name': 'Ghaziabad', 'state': 'Uttar Pradesh', 'price': 8000, 'growth': 0.06, 'population': 1636068, 'tier': 'Tier 2'},
            {'name': 'Ludhiana', 'state': 'Punjab', 'price': 7000, 'growth': 0.05, 'population': 1618879, 'tier': 'Tier 2'},
            {'name': 'Agra', 'state': 'Uttar Pradesh', 'price': 4500, 'growth': 0.05, 'population': 1585704, 'tier': 'Tier 2'},
            {'name': 'Nashik', 'state': 'Maharashtra', 'price': 6000, 'growth': 0.06, 'population': 1486973, 'tier': 'Tier 2'},
            {'name': 'Faridabad', 'state': 'Haryana', 'price': 9000, 'growth': 0.06, 'population': 1414050, 'tier': 'Tier 2'},
            {'name': 'Meerut', 'state': 'Uttar Pradesh', 'price': 5000, 'growth': 0.05, 'population': 1305429, 'tier': 'Tier 2'},
            {'name': 'Rajkot', 'state': 'Gujarat', 'price': 5500, 'growth': 0.06, 'population': 1286995, 'tier': 'Tier 2'},
            {'name': 'Kalyan-Dombivli', 'state': 'Maharashtra', 'price': 14000, 'growth': 0.07, 'population': 1246381, 'tier': 'Tier 2'},
            {'name': 'Vasai-Virar', 'state': 'Maharashtra', 'price': 12000, 'growth': 0.08, 'population': 1221233, 'tier': 'Tier 2'},
            {'name': 'Varanasi', 'state': 'Uttar Pradesh', 'price': 4000, 'growth': 0.05, 'population': 1201815, 'tier': 'Tier 2'},
            
            # Tier 3 cities
            {'name': 'Amritsar', 'state': 'Punjab', 'price': 5500, 'growth': 0.05, 'population': 1183705, 'tier': 'Tier 3'},
            {'name': 'Aligarh', 'state': 'Uttar Pradesh', 'price': 3500, 'growth': 0.04, 'population': 874408, 'tier': 'Tier 3'},
            {'name': 'Guwahati', 'state': 'Assam', 'price': 4500, 'growth': 0.05, 'population': 962334, 'tier': 'Tier 3'},
            {'name': 'Chandigarh', 'state': 'Chandigarh', 'price': 12000, 'growth': 0.06, 'population': 1025682, 'tier': 'Tier 3'},
            {'name': 'Thiruvananthapuram', 'state': 'Kerala', 'price': 6000, 'growth': 0.05, 'population': 957730, 'tier': 'Tier 3'},
            {'name': 'Solapur', 'state': 'Maharashtra', 'price': 4000, 'growth': 0.05, 'population': 951118, 'tier': 'Tier 3'},
            {'name': 'Madurai', 'state': 'Tamil Nadu', 'price': 5000, 'growth': 0.05, 'population': 1017865, 'tier': 'Tier 3'},
            {'name': 'Coimbatore', 'state': 'Tamil Nadu', 'price': 6500, 'growth': 0.06, 'population': 1061447, 'tier': 'Tier 3'},
            {'name': 'Jodhpur', 'state': 'Rajasthan', 'price': 4500, 'growth': 0.05, 'population': 1033756, 'tier': 'Tier 3'},
            {'name': 'Kota', 'state': 'Rajasthan', 'price': 4000, 'growth': 0.05, 'population': 1001365, 'tier': 'Tier 3'},
            {'name': 'Gwalior', 'state': 'Madhya Pradesh', 'price': 3500, 'growth': 0.04, 'population': 1101981, 'tier': 'Tier 3'},
            {'name': 'Vijayawada', 'state': 'Andhra Pradesh', 'price': 5500, 'growth': 0.06, 'population': 1048240, 'tier': 'Tier 3'},
            {'name': 'Mysore', 'state': 'Karnataka', 'price': 6000, 'growth': 0.05, 'population': 920550, 'tier': 'Tier 3'},
            {'name': 'Bareilly', 'state': 'Uttar Pradesh', 'price': 3000, 'growth': 0.04, 'population': 903668, 'tier': 'Tier 3'},
            {'name': 'Allahabad', 'state': 'Uttar Pradesh', 'price': 3500, 'growth': 0.04, 'population': 1216719, 'tier': 'Tier 3'},
            {'name': 'Jabalpur', 'state': 'Madhya Pradesh', 'price': 3500, 'growth': 0.04, 'population': 1267564, 'tier': 'Tier 3'},
            {'name': 'Ranchi', 'state': 'Jharkhand', 'price': 4000, 'growth': 0.05, 'population': 1073440, 'tier': 'Tier 3'},
            {'name': 'Howrah', 'state': 'West Bengal', 'price': 6000, 'growth': 0.05, 'population': 1077075, 'tier': 'Tier 3'},
            {'name': 'Jalandhar', 'state': 'Punjab', 'price': 5000, 'growth': 0.05, 'population': 873725, 'tier': 'Tier 3'},
            {'name': 'Tiruchirappalli', 'state': 'Tamil Nadu', 'price': 4500, 'growth': 0.05, 'population': 916857, 'tier': 'Tier 3'},
        ]
        
        for city_data in cities_data:
            city = City(
                name=city_data['name'],
                state=city_data['state'],
                base_price_per_sqft=city_data['price'],
                growth_rate=city_data['growth'],
                population=city_data['population'],
                tier=city_data['tier']
            )
            db.session.add(city)
        
        db.session.commit()  # Commit cities first to get IDs
        
        # Seed localities for major cities
        localities_data = [
            # Mumbai localities
            {'city': 'Mumbai', 'name': 'Bandra West', 'price': 45000, 'multiplier': 1.8, 'type': 'residential', 'pin': '400050'},
            {'city': 'Mumbai', 'name': 'Juhu', 'price': 50000, 'multiplier': 2.0, 'type': 'residential', 'pin': '400049'},
            {'city': 'Mumbai', 'name': 'Lower Parel', 'price': 55000, 'multiplier': 2.2, 'type': 'commercial', 'pin': '400013'},
            {'city': 'Mumbai', 'name': 'Andheri East', 'price': 35000, 'multiplier': 1.4, 'type': 'residential', 'pin': '400069'},
            {'city': 'Mumbai', 'name': 'Powai', 'price': 38000, 'multiplier': 1.5, 'type': 'residential', 'pin': '400076'},
            {'city': 'Mumbai', 'name': 'Worli', 'price': 60000, 'multiplier': 2.4, 'type': 'residential', 'pin': '400018'},
            {'city': 'Mumbai', 'name': 'Malad West', 'price': 28000, 'multiplier': 1.1, 'type': 'residential', 'pin': '400064'},
            {'city': 'Mumbai', 'name': 'Goregaon East', 'price': 30000, 'multiplier': 1.2, 'type': 'residential', 'pin': '400063'},
            
            # Delhi localities
            {'city': 'Delhi', 'name': 'Connaught Place', 'price': 80000, 'multiplier': 3.6, 'type': 'commercial', 'pin': '110001'},
            {'city': 'Delhi', 'name': 'Defence Colony', 'price': 45000, 'multiplier': 2.0, 'type': 'residential', 'pin': '110024'},
            {'city': 'Delhi', 'name': 'Greater Kailash', 'price': 40000, 'multiplier': 1.8, 'type': 'residential', 'pin': '110048'},
            {'city': 'Delhi', 'name': 'Saket', 'price': 38000, 'multiplier': 1.7, 'type': 'residential', 'pin': '110017'},
            {'city': 'Delhi', 'name': 'Vasant Vihar', 'price': 50000, 'multiplier': 2.3, 'type': 'residential', 'pin': '110057'},
            {'city': 'Delhi', 'name': 'Dwarka', 'price': 25000, 'multiplier': 1.1, 'type': 'residential', 'pin': '110075'},
            {'city': 'Delhi', 'name': 'Rohini', 'price': 20000, 'multiplier': 0.9, 'type': 'residential', 'pin': '110085'},
            {'city': 'Delhi', 'name': 'Gurgaon Sector 28', 'price': 35000, 'multiplier': 1.6, 'type': 'commercial', 'pin': '122002'},
            
            # Bangalore localities
            {'city': 'Bangalore', 'name': 'Koramangala', 'price': 28000, 'multiplier': 1.6, 'type': 'residential', 'pin': '560034'},
            {'city': 'Bangalore', 'name': 'Indiranagar', 'price': 25000, 'multiplier': 1.4, 'type': 'residential', 'pin': '560038'},
            {'city': 'Bangalore', 'name': 'Whitefield', 'price': 22000, 'multiplier': 1.2, 'type': 'residential', 'pin': '560066'},
            {'city': 'Bangalore', 'name': 'Electronic City', 'price': 18000, 'multiplier': 1.0, 'type': 'commercial', 'pin': '560100'},
            {'city': 'Bangalore', 'name': 'Jayanagar', 'price': 20000, 'multiplier': 1.1, 'type': 'residential', 'pin': '560011'},
            {'city': 'Bangalore', 'name': 'HSR Layout', 'price': 24000, 'multiplier': 1.3, 'type': 'residential', 'pin': '560102'},
            {'city': 'Bangalore', 'name': 'Marathahalli', 'price': 20000, 'multiplier': 1.1, 'type': 'residential', 'pin': '560037'},
            {'city': 'Bangalore', 'name': 'Sarjapur Road', 'price': 16000, 'multiplier': 0.9, 'type': 'residential', 'pin': '560035'},
            
            # Hyderabad localities
            {'city': 'Hyderabad', 'name': 'Banjara Hills', 'price': 25000, 'multiplier': 1.7, 'type': 'residential', 'pin': '500034'},
            {'city': 'Hyderabad', 'name': 'Jubilee Hills', 'price': 28000, 'multiplier': 1.9, 'type': 'residential', 'pin': '500033'},
            {'city': 'Hyderabad', 'name': 'Gachibowli', 'price': 18000, 'multiplier': 1.2, 'type': 'commercial', 'pin': '500032'},
            {'city': 'Hyderabad', 'name': 'Hitech City', 'price': 20000, 'multiplier': 1.3, 'type': 'commercial', 'pin': '500081'},
            {'city': 'Hyderabad', 'name': 'Kondapur', 'price': 16000, 'multiplier': 1.1, 'type': 'residential', 'pin': '500084'},
            {'city': 'Hyderabad', 'name': 'Madhapur', 'price': 18000, 'multiplier': 1.2, 'type': 'residential', 'pin': '500081'},
            
            # Chennai localities
            {'city': 'Chennai', 'name': 'T Nagar', 'price': 22000, 'multiplier': 1.6, 'type': 'commercial', 'pin': '600017'},
            {'city': 'Chennai', 'name': 'Anna Nagar', 'price': 18000, 'multiplier': 1.3, 'type': 'residential', 'pin': '600040'},
            {'city': 'Chennai', 'name': 'Adyar', 'price': 20000, 'multiplier': 1.4, 'type': 'residential', 'pin': '600020'},
            {'city': 'Chennai', 'name': 'Velachery', 'price': 15000, 'multiplier': 1.1, 'type': 'residential', 'pin': '600042'},
            {'city': 'Chennai', 'name': 'OMR', 'price': 16000, 'multiplier': 1.1, 'type': 'commercial', 'pin': '600096'},
            {'city': 'Chennai', 'name': 'Porur', 'price': 14000, 'multiplier': 1.0, 'type': 'residential', 'pin': '600116'},
            
            # Pune localities
            {'city': 'Pune', 'name': 'Koregaon Park', 'price': 25000, 'multiplier': 1.6, 'type': 'residential', 'pin': '411001'},
            {'city': 'Pune', 'name': 'Baner', 'price': 18000, 'multiplier': 1.1, 'type': 'residential', 'pin': '411045'},
            {'city': 'Pune', 'name': 'Hinjewadi', 'price': 16000, 'multiplier': 1.0, 'type': 'commercial', 'pin': '411057'},
            {'city': 'Pune', 'name': 'Wakad', 'price': 15000, 'multiplier': 0.9, 'type': 'residential', 'pin': '411057'},
            {'city': 'Pune', 'name': 'Kharadi', 'price': 17000, 'multiplier': 1.1, 'type': 'residential', 'pin': '411014'},
        ]
        
        for locality_data in localities_data:
            city = City.query.filter_by(name=locality_data['city']).first()
            if city:
                locality = Locality(
                    name=locality_data['name'],
                    city_id=city.id,
                    price_per_sqft=locality_data['price'],
                    location_multiplier=locality_data['multiplier'],
                    area_type=locality_data['type'],
                    pin_code=locality_data['pin']
                )
                db.session.add(locality)
        
        # Seed infrastructure multipliers
        multipliers_data = [
            # Road width multipliers
            {'type': 'road_width', 'value': '0-12', 'multiplier': 0.9, 'desc': 'Narrow roads, limited access'},
            {'type': 'road_width', 'value': '12-20', 'multiplier': 1.0, 'desc': 'Standard residential roads'},
            {'type': 'road_width', 'value': '20-30', 'multiplier': 1.1, 'desc': 'Wide residential roads'},
            {'type': 'road_width', 'value': '30-40', 'multiplier': 1.2, 'desc': 'Major roads with good connectivity'},
            {'type': 'road_width', 'value': '>40', 'multiplier': 1.3, 'desc': 'Highway frontage or main arterials'},
            
            # Infrastructure multipliers
            {'type': 'nearby_schools', 'value': 'yes', 'multiplier': 1.1, 'desc': 'Good schools within 2km'},
            {'type': 'nearby_schools', 'value': 'no', 'multiplier': 1.0, 'desc': 'No major schools nearby'},
            {'type': 'nearby_metro', 'value': 'yes', 'multiplier': 1.25, 'desc': 'Metro station within 1km'},
            {'type': 'nearby_metro', 'value': 'no', 'multiplier': 1.0, 'desc': 'No metro connectivity'},
            {'type': 'commercial_area', 'value': 'yes', 'multiplier': 1.15, 'desc': 'Commercial hub nearby'},
            {'type': 'commercial_area', 'value': 'no', 'multiplier': 1.0, 'desc': 'Primarily residential area'},
            
            # Proximity multipliers
            {'type': 'airport_proximity', 'value': '<10km', 'multiplier': 1.2, 'desc': 'Close to airport'},
            {'type': 'airport_proximity', 'value': '10-25km', 'multiplier': 1.1, 'desc': 'Moderate distance to airport'},
            {'type': 'airport_proximity', 'value': '>25km', 'multiplier': 1.0, 'desc': 'Far from airport'},
            {'type': 'it_park_proximity', 'value': '<5km', 'multiplier': 1.15, 'desc': 'Close to IT parks'},
            {'type': 'it_park_proximity', 'value': '5-15km', 'multiplier': 1.05, 'desc': 'Moderate distance to IT parks'},
            {'type': 'it_park_proximity', 'value': '>15km', 'multiplier': 1.0, 'desc': 'Far from IT parks'},
        ]
        
        for mult_data in multipliers_data:
            multiplier = InfrastructureMultiplier(
                factor_type=mult_data['type'],
                factor_value=mult_data['value'],
                multiplier=mult_data['multiplier'],
                description=mult_data['desc']
            )
            db.session.add(multiplier)
        
        # Create a default API key
        default_api_key = APIKey(
            key=secrets.token_urlsafe(32),
            name='Default API Key',
            rate_limit=50
        )
        db.session.add(default_api_key)
        
        db.session.commit()
        logging.info("Initial data seeded successfully!")
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error seeding initial data: {e}")
