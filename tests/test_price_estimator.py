import unittest
import os
import sys
from datetime import datetime

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import City, Locality, InfrastructureMultiplier
from price_estimator import PriceEstimator

class TestPriceEstimator(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        self.app_context = app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test data
        self.setup_test_data()
        
        # Initialize price estimator
        self.estimator = PriceEstimator()
    
    def tearDown(self):
        """Clean up after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def setup_test_data(self):
        """Create test data for price estimation testing."""
        # Create test cities
        cities = [
            City(
                name='Mumbai',
                state='Maharashtra',
                base_price_per_sqft=25000,
                growth_rate=0.08,
                population=12442373,
                tier='Tier 1'
            ),
            City(
                name='Test City',
                state='Test State',
                base_price_per_sqft=5000,
                growth_rate=0.06,
                population=1000000,
                tier='Tier 2'
            ),
            City(
                name='Small City',
                state='Test State',
                base_price_per_sqft=3000,
                growth_rate=0.04,
                population=500000,
                tier='Tier 3'
            )
        ]
        
        for city in cities:
            db.session.add(city)
        
        db.session.commit()
        
        # Create test localities
        mumbai = City.query.filter_by(name='Mumbai').first()
        test_city = City.query.filter_by(name='Test City').first()
        
        localities = [
            Locality(
                name='Bandra West',
                city_id=mumbai.id,
                price_per_sqft=45000,
                location_multiplier=1.8,
                area_type='residential',
                pin_code='400050'
            ),
            Locality(
                name='Test Locality',
                city_id=test_city.id,
                price_per_sqft=6000,
                location_multiplier=1.2,
                area_type='residential',
                pin_code='123456'
            ),
            Locality(
                name='Commercial Area',
                city_id=test_city.id,
                price_per_sqft=8000,
                location_multiplier=1.5,
                area_type='commercial',
                pin_code='123457'
            )
        ]
        
        for locality in localities:
            db.session.add(locality)
        
        # Create test infrastructure multipliers
        multipliers = [
            InfrastructureMultiplier(
                factor_type='road_width',
                factor_value='0-12',
                multiplier=0.9,
                description='Narrow roads'
            ),
            InfrastructureMultiplier(
                factor_type='road_width',
                factor_value='20-30',
                multiplier=1.1,
                description='Wide roads'
            ),
            InfrastructureMultiplier(
                factor_type='road_width',
                factor_value='>40',
                multiplier=1.3,
                description='Highway frontage'
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
                description='Metro station nearby'
            ),
            InfrastructureMultiplier(
                factor_type='commercial_area',
                factor_value='yes',
                multiplier=1.15,
                description='Commercial hub nearby'
            )
        ]
        
        for mult in multipliers:
            db.session.add(mult)
        
        db.session.commit()
    
    def test_basic_estimation(self):
        """Test basic price estimation functionality."""
        result = self.estimator.estimate_price(
            state='Maharashtra',
            city_name='Mumbai',
            plot_size_sqft=1000
        )
        
        self.assertIn('estimated_price_per_sqft', result)
        self.assertIn('total_estimated_price', result)
        self.assertIn('confidence_score', result)
        self.assertIn('data_sources', result)
        self.assertIn('calculation_breakdown', result)
        
        # Check that total price = price_per_sqft * plot_size
        self.assertAlmostEqual(
            result['total_estimated_price'],
            result['estimated_price_per_sqft'] * 1000,
            places=2
        )
    
    def test_locality_specific_estimation(self):
        """Test price estimation with locality data."""
        # Test with locality
        result_with_locality = self.estimator.estimate_price(
            state='Maharashtra',
            city_name='Mumbai',
            locality_name='Bandra West',
            plot_size_sqft=1000
        )
        
        # Test without locality
        result_without_locality = self.estimator.estimate_price(
            state='Maharashtra',
            city_name='Mumbai',
            plot_size_sqft=1000
        )
        
        # With locality should have higher confidence
        self.assertGreater(
            result_with_locality['confidence_score'],
            result_without_locality['confidence_score']
        )
        
        # With locality should use locality price
        self.assertGreater(
            result_with_locality['estimated_price_per_sqft'],
            result_without_locality['estimated_price_per_sqft']
        )
    
    def test_infrastructure_multipliers(self):
        """Test infrastructure multiplier calculations."""
        # Test without infrastructure
        result_basic = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=1000
        )
        
        # Test with positive infrastructure
        result_with_infra = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=1000,
            road_width_ft=25,
            nearby_schools=True,
            nearby_metro=True,
            commercial_area=True
        )
        
        # Infrastructure should increase the price
        self.assertGreater(
            result_with_infra['estimated_price_per_sqft'],
            result_basic['estimated_price_per_sqft']
        )
        
        # Infrastructure multiplier should be > 1
        self.assertGreater(
            result_with_infra['calculation_breakdown']['infrastructure_multiplier'],
            1.0
        )
    
    def test_road_width_multipliers(self):
        """Test different road width multiplier calculations."""
        test_cases = [
            (10, 0.9),    # Narrow road
            (15, 1.0),    # Standard road
            (25, 1.1),    # Wide road
            (45, 1.3),    # Highway frontage
        ]
        
        for road_width, expected_min_multiplier in test_cases:
            result = self.estimator.estimate_price(
                state='Test State',
                city_name='Test City',
                plot_size_sqft=1000,
                road_width_ft=road_width
            )
            
            infra_multiplier = result['calculation_breakdown']['infrastructure_multiplier']
            
            # Check that the multiplier is in the expected range
            if road_width <= 12:
                self.assertLessEqual(infra_multiplier, 1.0)
            elif road_width >= 40:
                self.assertGreaterEqual(infra_multiplier, 1.2)
    
    def test_year_trend_calculation(self):
        """Test year trend factor calculations."""
        base_year = 2024
        
        # Test past year
        result_past = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=1000,
            year=2022
        )
        
        # Test current year
        result_current = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=1000,
            year=base_year
        )
        
        # Test future year
        result_future = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=1000,
            year=2026
        )
        
        # Past year should have lower price than current
        self.assertLess(
            result_past['estimated_price_per_sqft'],
            result_current['estimated_price_per_sqft']
        )
        
        # Future year should have higher price than current
        self.assertGreater(
            result_future['estimated_price_per_sqft'],
            result_current['estimated_price_per_sqft']
        )
    
    def test_area_type_multipliers(self):
        """Test different area type multipliers."""
        area_types = {
            'residential': 1.0,
            'commercial': 1.8,
            'agricultural': 0.3,
            'industrial': 1.5
        }
        
        base_result = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=1000,
            area_type='residential'
        )
        
        for area_type, expected_multiplier in area_types.items():
            result = self.estimator.estimate_price(
                state='Test State',
                city_name='Test City',
                plot_size_sqft=1000,
                area_type=area_type
            )
            
            actual_multiplier = result['calculation_breakdown']['area_type_multiplier']
            self.assertEqual(actual_multiplier, expected_multiplier)
            
            # Commercial should be most expensive, agricultural cheapest
            if area_type == 'commercial':
                self.assertGreater(
                    result['estimated_price_per_sqft'],
                    base_result['estimated_price_per_sqft'] * 1.5
                )
            elif area_type == 'agricultural':
                self.assertLess(
                    result['estimated_price_per_sqft'],
                    base_result['estimated_price_per_sqft'] * 0.5
                )
    
    def test_city_tier_impact(self):
        """Test impact of city tier on location multiplier."""
        # Tier 1 city
        result_tier1 = self.estimator.estimate_price(
            state='Maharashtra',
            city_name='Mumbai',
            plot_size_sqft=1000
        )
        
        # Tier 2 city
        result_tier2 = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=1000
        )
        
        # Tier 3 city
        result_tier3 = self.estimator.estimate_price(
            state='Test State',
            city_name='Small City',
            plot_size_sqft=1000
        )
        
        # Higher tier cities should generally have higher multipliers
        # (though base prices are already different, multipliers also vary)
        tier1_mult = result_tier1['calculation_breakdown']['location_multiplier']
        tier2_mult = result_tier2['calculation_breakdown']['location_multiplier']
        tier3_mult = result_tier3['calculation_breakdown']['location_multiplier']
        
        self.assertGreaterEqual(tier1_mult, tier2_mult)
        self.assertGreaterEqual(tier2_mult, tier3_mult)
    
    def test_fallback_estimation(self):
        """Test fallback estimation for unknown cities."""
        result = self.estimator.estimate_price(
            state='Unknown State',
            city_name='Unknown City',
            plot_size_sqft=1000
        )
        
        # Should return a result even for unknown city
        self.assertIn('estimated_price_per_sqft', result)
        self.assertIn('total_estimated_price', result)
        
        # Confidence should be low for fallback
        self.assertLess(result['confidence_score'], 0.5)
        
        # Should use state average
        self.assertIn('State average', result['data_sources'][0])
    
    def test_calculation_breakdown_completeness(self):
        """Test that calculation breakdown contains all required components."""
        result = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=1000,
            road_width_ft=25,
            nearby_schools=True,
            nearby_metro=True,
            year=2025,
            area_type='commercial'
        )
        
        breakdown = result['calculation_breakdown']
        
        required_components = [
            'base_price_per_sqft',
            'location_multiplier',
            'infrastructure_multiplier',
            'year_trend_factor',
            'area_type_multiplier'
        ]
        
        for component in required_components:
            self.assertIn(component, breakdown)
            self.assertIsInstance(breakdown[component], (int, float))
            self.assertGreater(breakdown[component], 0)
        
        # Verify calculation
        expected_price = (
            breakdown['base_price_per_sqft'] *
            breakdown['location_multiplier'] *
            breakdown['infrastructure_multiplier'] *
            breakdown['year_trend_factor'] *
            breakdown['area_type_multiplier']
        )
        
        self.assertAlmostEqual(
            result['estimated_price_per_sqft'],
            expected_price,
            places=2
        )
    
    def test_range_matching_function(self):
        """Test the range matching helper function."""
        # Test range matching
        self.assertTrue(self.estimator._check_range_match(25, '20-30'))
        self.assertFalse(self.estimator._check_range_match(15, '20-30'))
        
        # Test greater than
        self.assertTrue(self.estimator._check_range_match(50, '>40'))
        self.assertFalse(self.estimator._check_range_match(30, '>40'))
        
        # Test less than
        self.assertTrue(self.estimator._check_range_match(10, '<15'))
        self.assertFalse(self.estimator._check_range_match(20, '<15'))
        
        # Test exact match
        self.assertTrue(self.estimator._check_range_match(25, '25'))
        self.assertFalse(self.estimator._check_range_match(24, '25'))
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Very small plot size
        result = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=1
        )
        self.assertGreater(result['total_estimated_price'], 0)
        
        # Very large plot size
        result = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=100000
        )
        self.assertGreater(result['total_estimated_price'], 0)
        
        # Extreme road width
        result = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=1000,
            road_width_ft=200
        )
        self.assertGreater(result['estimated_price_per_sqft'], 0)
        
        # Current year
        current_year = datetime.now().year
        result = self.estimator.estimate_price(
            state='Test State',
            city_name='Test City',
            plot_size_sqft=1000,
            year=current_year
        )
        self.assertGreater(result['estimated_price_per_sqft'], 0)

if __name__ == '__main__':
    unittest.main()
