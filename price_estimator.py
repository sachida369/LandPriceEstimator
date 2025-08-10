import math
from datetime import datetime
from models import City, Locality, InfrastructureMultiplier
from config import Config

class PriceEstimator:
    def __init__(self):
        self.base_year = Config.BASE_YEAR
        self.inflation_rate = Config.INFLATION_RATE
    
    def estimate_price(self, state, city_name, locality_name=None, plot_size_sqft=1000, 
                      road_width_ft=20, nearby_schools=False, nearby_metro=False, 
                      commercial_area=False, year=None, area_type='residential'):
        """
        Estimate land price based on location and infrastructure factors
        """
        if year is None:
            year = datetime.now().year
        
        # Get base price from database
        city = City.query.filter_by(name=city_name, state=state).first()
        if not city:
            return self._fallback_estimate(state, city_name, plot_size_sqft, year)
        
        base_price = city.base_price_per_sqft
        confidence_score = 0.7  # Base confidence for city-level data
        data_sources = [f"City: {city_name}"]
        
        # Try to get locality-specific price
        if locality_name:
            locality = Locality.query.filter_by(name=locality_name, city_id=city.id).first()
            if locality:
                base_price = locality.price_per_sqft
                confidence_score = 0.9  # Higher confidence for locality data
                data_sources.append(f"Locality: {locality_name}")
            else:
                confidence_score = 0.6  # Lower confidence when locality not found
        
        # Calculate location multiplier
        location_multiplier = self._calculate_location_multiplier(city, locality_name)
        
        # Calculate infrastructure multiplier
        infra_multiplier = self._calculate_infrastructure_multiplier(
            road_width_ft, nearby_schools, nearby_metro, commercial_area
        )
        
        # Calculate year trend factor
        year_trend_factor = self._calculate_year_trend_factor(year, city.growth_rate)
        
        # Apply area type multiplier
        area_type_multiplier = self._get_area_type_multiplier(area_type)
        
        # Final calculation
        estimated_price_per_sqft = (base_price * location_multiplier * 
                                   infra_multiplier * year_trend_factor * 
                                   area_type_multiplier)
        
        total_estimated_price = estimated_price_per_sqft * plot_size_sqft
        
        return {
            'estimated_price_per_sqft': round(estimated_price_per_sqft, 2),
            'total_estimated_price': round(total_estimated_price, 2),
            'confidence_score': round(confidence_score, 2),
            'data_sources': data_sources,
            'calculation_breakdown': {
                'base_price_per_sqft': round(base_price, 2),
                'location_multiplier': round(location_multiplier, 2),
                'infrastructure_multiplier': round(infra_multiplier, 2),
                'year_trend_factor': round(year_trend_factor, 2),
                'area_type_multiplier': round(area_type_multiplier, 2)
            }
        }
    
    def _calculate_location_multiplier(self, city, locality_name):
        """Calculate multiplier based on city tier and locality demand"""
        base_multiplier = 1.0
        
        # City tier multiplier
        tier_multipliers = {
            'Tier 1': 1.5,
            'Tier 2': 1.2,
            'Tier 3': 1.0,
            'Tier 4': 0.8
        }
        
        if city.tier in tier_multipliers:
            base_multiplier *= tier_multipliers[city.tier]
        
        # Population-based adjustment
        if city.population:
            if city.population > 10000000:  # >10M
                base_multiplier *= 1.3
            elif city.population > 5000000:  # 5-10M
                base_multiplier *= 1.2
            elif city.population > 1000000:  # 1-5M
                base_multiplier *= 1.1
        
        return base_multiplier
    
    def _calculate_infrastructure_multiplier(self, road_width_ft, nearby_schools, 
                                           nearby_metro, commercial_area):
        """Calculate multiplier based on infrastructure factors"""
        multiplier = 1.0
        
        # Road width factor
        road_multipliers = InfrastructureMultiplier.query.filter_by(
            factor_type='road_width'
        ).all()
        
        for rm in road_multipliers:
            if self._check_range_match(road_width_ft, rm.factor_value):
                multiplier *= rm.multiplier
                break
        else:
            # Default road width calculation if not in database
            if road_width_ft >= 40:
                multiplier *= 1.3
            elif road_width_ft >= 30:
                multiplier *= 1.2
            elif road_width_ft >= 20:
                multiplier *= 1.1
            elif road_width_ft < 12:
                multiplier *= 0.9
        
        # Nearby amenities
        if nearby_schools:
            school_mult = InfrastructureMultiplier.query.filter_by(
                factor_type='nearby_schools', factor_value='yes'
            ).first()
            multiplier *= school_mult.multiplier if school_mult else 1.1
        
        if nearby_metro:
            metro_mult = InfrastructureMultiplier.query.filter_by(
                factor_type='nearby_metro', factor_value='yes'
            ).first()
            multiplier *= metro_mult.multiplier if metro_mult else 1.25
        
        if commercial_area:
            commercial_mult = InfrastructureMultiplier.query.filter_by(
                factor_type='commercial_area', factor_value='yes'
            ).first()
            multiplier *= commercial_mult.multiplier if commercial_mult else 1.15
        
        return multiplier
    
    def _calculate_year_trend_factor(self, target_year, city_growth_rate):
        """Calculate year trend factor based on inflation and growth"""
        year_diff = target_year - self.base_year
        
        # Combine inflation and city-specific growth
        combined_rate = self.inflation_rate + city_growth_rate
        
        return math.pow(1 + combined_rate, year_diff)
    
    def _get_area_type_multiplier(self, area_type):
        """Get multiplier based on area type"""
        multipliers = {
            'residential': 1.0,
            'commercial': 1.8,
            'agricultural': 0.3,
            'industrial': 1.5
        }
        return multipliers.get(area_type, 1.0)
    
    def _check_range_match(self, value, range_str):
        """Check if a value matches a range string like '20-30' or '>40'"""
        try:
            if '-' in range_str:
                min_val, max_val = map(float, range_str.split('-'))
                return min_val <= value <= max_val
            elif range_str.startswith('>'):
                threshold = float(range_str[1:])
                return value > threshold
            elif range_str.startswith('<'):
                threshold = float(range_str[1:])
                return value < threshold
            else:
                return float(range_str) == value
        except:
            return False
    
    def _fallback_estimate(self, state, city_name, plot_size_sqft, year):
        """Fallback estimation when city data is not available"""
        # Use state averages or national averages
        state_averages = {
            'Maharashtra': 8000,
            'Karnataka': 6500,
            'Delhi': 25000,
            'Tamil Nadu': 5500,
            'Gujarat': 4500,
            'Rajasthan': 3500,
            'Uttar Pradesh': 3000,
            'West Bengal': 4000,
            'Punjab': 4200,
            'Haryana': 6000
        }
        
        base_price = state_averages.get(state, 3500)  # National average fallback
        
        # Apply basic year trend
        year_diff = year - self.base_year
        year_factor = math.pow(1 + self.inflation_rate, year_diff)
        
        estimated_price_per_sqft = base_price * year_factor
        total_estimated_price = estimated_price_per_sqft * plot_size_sqft
        
        return {
            'estimated_price_per_sqft': round(estimated_price_per_sqft, 2),
            'total_estimated_price': round(total_estimated_price, 2),
            'confidence_score': 0.3,  # Low confidence for fallback
            'data_sources': [f"State average: {state}"],
            'calculation_breakdown': {
                'base_price_per_sqft': round(base_price, 2),
                'location_multiplier': 1.0,
                'infrastructure_multiplier': 1.0,
                'year_trend_factor': round(year_factor, 2),
                'area_type_multiplier': 1.0
            }
        }
