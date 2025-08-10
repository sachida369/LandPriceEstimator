import unittest
import json
import os
import sys

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import City, Locality, APIKey, InfrastructureMultiplier
import secrets

class TestAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test data
        self.setup_test_data()
    
    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def setup_test_data(self):
        """Create test data for API testing."""
        # Create test city
        city = City(
            name='Test City',
            state='Test State',
            base_price_per_sqft=5000,
            growth_rate=0.06,
            population=1000000,
            tier='Tier 2'
        )
        db.session.add(city)
        db.session.commit()
        
        # Create test locality
        locality = Locality(
            name='Test Locality',
            city_id=city.id,
            price_per_sqft=6000,
            location_multiplier=1.2,
            area_type='residential',
            pin_code='123456'
        )
        db.session.add(locality)
        
        # Create test infrastructure multipliers
        multipliers = [
            InfrastructureMultiplier(
                factor_type='road_width',
                factor_value='20-30',
                multiplier=1.1,
                description='Wide residential roads'
            ),
            InfrastructureMultiplier(
                factor_type='nearby_schools',
                factor_value='yes',
                multiplier=1.1,
                description='Good schools nearby'
            ),
            InfrastructureMultiplier(
                factor_type='nearby_metro',
                factor_value='yes',
                multiplier=1.25,
                description='Metro station within 1km'
            )
        ]
        
        for mult in multipliers:
            db.session.add(mult)
        
        # Create test API key
        self.api_key = APIKey(
            key='test_api_key_123',
            name='Test API Key',
            is_active=True,
            rate_limit=100
        )
        db.session.add(self.api_key)
        
        db.session.commit()
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'Land Price Estimator API')
    
    def test_estimate_without_api_key(self):
        """Test estimate endpoint without API key."""
        response = self.client.post('/api/estimate', 
                                   json={'state': 'Test State', 'city': 'Test City'})
        self.assertEqual(response.status_code, 401)
        
        data = json.loads(response.data)
        self.assertIn('API key is required', data['error'])
    
    def test_estimate_with_invalid_api_key(self):
        """Test estimate endpoint with invalid API key."""
        headers = {'X-API-Key': 'invalid_key'}
        response = self.client.post('/api/estimate',
                                   json={'state': 'Test State', 'city': 'Test City'},
                                   headers=headers)
        self.assertEqual(response.status_code, 401)
        
        data = json.loads(response.data)
        self.assertIn('Invalid API key', data['error'])
    
    def test_estimate_missing_required_params(self):
        """Test estimate endpoint with missing required parameters."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        # Missing city
        response = self.client.post('/api/estimate',
                                   json={'state': 'Test State'},
                                   headers=headers)
        self.assertEqual(response.status_code, 400)
        
        # Missing state
        response = self.client.post('/api/estimate',
                                   json={'city': 'Test City'},
                                   headers=headers)
        self.assertEqual(response.status_code, 400)
    
    def test_estimate_successful_basic(self):
        """Test successful basic price estimation."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        response = self.client.post('/api/estimate',
                                   json={
                                       'state': 'Test State',
                                       'city': 'Test City',
                                       'plot_size_sqft': 1000
                                   },
                                   headers=headers)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('estimated_price_per_sqft', data['data'])
        self.assertIn('total_estimated_price', data['data'])
        self.assertIn('confidence_score', data['data'])
        self.assertIn('calculation_breakdown', data['data'])
    
    def test_estimate_with_locality(self):
        """Test price estimation with locality specified."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        response = self.client.post('/api/estimate',
                                   json={
                                       'state': 'Test State',
                                       'city': 'Test City',
                                       'locality': 'Test Locality',
                                       'plot_size_sqft': 1000
                                   },
                                   headers=headers)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        # Should have higher confidence with locality data
        self.assertGreater(data['data']['confidence_score'], 0.8)
    
    def test_estimate_with_infrastructure(self):
        """Test price estimation with infrastructure factors."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        response = self.client.post('/api/estimate',
                                   json={
                                       'state': 'Test State',
                                       'city': 'Test City',
                                       'plot_size_sqft': 1000,
                                       'road_width_ft': 25,
                                       'nearby_schools': True,
                                       'nearby_metro': True,
                                       'commercial_area': False
                                   },
                                   headers=headers)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Infrastructure should increase the price
        breakdown = data['data']['calculation_breakdown']
        self.assertGreater(breakdown['infrastructure_multiplier'], 1.0)
    
    def test_estimate_invalid_parameters(self):
        """Test estimate endpoint with invalid parameters."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        # Invalid plot size
        response = self.client.post('/api/estimate',
                                   json={
                                       'state': 'Test State',
                                       'city': 'Test City',
                                       'plot_size_sqft': -100
                                   },
                                   headers=headers)
        self.assertEqual(response.status_code, 400)
        
        # Invalid year
        response = self.client.post('/api/estimate',
                                   json={
                                       'state': 'Test State',
                                       'city': 'Test City',
                                       'year': 2050
                                   },
                                   headers=headers)
        self.assertEqual(response.status_code, 400)
        
        # Invalid area type
        response = self.client.post('/api/estimate',
                                   json={
                                       'state': 'Test State',
                                       'city': 'Test City',
                                       'area_type': 'invalid_type'
                                   },
                                   headers=headers)
        self.assertEqual(response.status_code, 400)
    
    def test_estimate_get_method(self):
        """Test estimate endpoint with GET method."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        response = self.client.get('/api/estimate?state=Test State&city=Test City&plot_size_sqft=1000',
                                  headers=headers)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_cities_endpoint(self):
        """Test cities listing endpoint."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        response = self.client.get('/api/cities', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
        
        # Check city data structure
        city_data = data['data'][0]
        self.assertIn('name', city_data)
        self.assertIn('state', city_data)
        self.assertIn('base_price_per_sqft', city_data)
    
    def test_cities_endpoint_with_state_filter(self):
        """Test cities endpoint with state filter."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        response = self.client.get('/api/cities?state=Test State', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # All cities should be from the specified state
        for city in data['data']:
            self.assertEqual(city['state'], 'Test State')
    
    def test_localities_endpoint(self):
        """Test localities listing endpoint."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        response = self.client.get('/api/localities?city=Test City', headers=headers)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIsInstance(data['data'], list)
        
        if len(data['data']) > 0:
            locality_data = data['data'][0]
            self.assertIn('name', locality_data)
            self.assertIn('price_per_sqft', locality_data)
    
    def test_localities_endpoint_missing_city(self):
        """Test localities endpoint without city parameter."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        response = self.client.get('/api/localities', headers=headers)
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('city parameter is required', data['error'])
    
    def test_localities_endpoint_invalid_city(self):
        """Test localities endpoint with non-existent city."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        response = self.client.get('/api/localities?city=Non Existent City', headers=headers)
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('City not found', data['error'])
    
    def test_fallback_estimation(self):
        """Test fallback estimation for unknown city."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        response = self.client.post('/api/estimate',
                                   json={
                                       'state': 'Unknown State',
                                       'city': 'Unknown City',
                                       'plot_size_sqft': 1000
                                   },
                                   headers=headers)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        # Should have lower confidence for fallback
        self.assertLess(data['data']['confidence_score'], 0.5)
    
    def test_year_trend_calculation(self):
        """Test year trend factor in price calculation."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        # Test future year
        response = self.client.post('/api/estimate',
                                   json={
                                       'state': 'Test State',
                                       'city': 'Test City',
                                       'plot_size_sqft': 1000,
                                       'year': 2026
                                   },
                                   headers=headers)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        breakdown = data['data']['calculation_breakdown']
        # Future year should have trend factor > 1
        self.assertGreater(breakdown['year_trend_factor'], 1.0)
    
    def test_area_type_multiplier(self):
        """Test different area type multipliers."""
        headers = {'X-API-Key': 'test_api_key_123'}
        
        area_types = ['residential', 'commercial', 'agricultural', 'industrial']
        
        for area_type in area_types:
            response = self.client.post('/api/estimate',
                                       json={
                                           'state': 'Test State',
                                           'city': 'Test City',
                                           'plot_size_sqft': 1000,
                                           'area_type': area_type
                                       },
                                       headers=headers)
            
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            breakdown = data['data']['calculation_breakdown']
            
            # Different area types should have different multipliers
            if area_type == 'commercial':
                self.assertGreater(breakdown['area_type_multiplier'], 1.5)
            elif area_type == 'agricultural':
                self.assertLess(breakdown['area_type_multiplier'], 0.5)

if __name__ == '__main__':
    unittest.main()
