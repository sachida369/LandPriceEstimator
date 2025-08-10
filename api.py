from flask import Blueprint, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import logging
from models import APIKey, PriceEstimate
from price_estimator import PriceEstimator
from app import limiter

api_bp = Blueprint('api', __name__)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'API key is required'}), 401
        
        key_record = APIKey.query.filter_by(key=api_key, is_active=True).first()
        if not key_record:
            return jsonify({'error': 'Invalid API key'}), 401
        
        g.api_key = key_record
        return f(*args, **kwargs)
    
    return decorated_function

@api_bp.route('/estimate', methods=['POST', 'GET'])
@limiter.limit("50 per hour")
@require_api_key
def api_estimate():
    """
    API endpoint for price estimation
    
    POST/GET /api/estimate
    Parameters:
    - state: string (required)
    - city: string (required)
    - locality: string (optional)
    - plot_size_sqft: float (default: 1000)
    - road_width_ft: float (default: 20)
    - nearby_schools: boolean (default: false)
    - nearby_metro: boolean (default: false)
    - commercial_area: boolean (default: false)
    - year: integer (default: current year)
    - area_type: string (default: residential)
    """
    
    try:
        # Get parameters from request
        if request.method == 'POST':
            data = request.get_json() or request.form.to_dict()
        else:
            data = request.args.to_dict()
        
        # Validate required parameters
        state = data.get('state')
        city = data.get('city')
        
        if not state or not city:
            return jsonify({
                'error': 'Missing required parameters',
                'required': ['state', 'city'],
                'message': 'State and city are required for price estimation'
            }), 400
        
        # Extract optional parameters with defaults
        locality = data.get('locality')
        
        try:
            plot_size = float(data.get('plot_size_sqft', 1000))
            road_width = float(data.get('road_width_ft', 20))
            year = int(data.get('year', 2024))
        except ValueError:
            return jsonify({
                'error': 'Invalid parameter types',
                'message': 'plot_size_sqft, road_width_ft must be numbers, year must be integer'
            }), 400
        
        # Validate ranges
        if plot_size <= 0:
            return jsonify({'error': 'plot_size_sqft must be greater than 0'}), 400
        
        if road_width < 0:
            return jsonify({'error': 'road_width_ft cannot be negative'}), 400
        
        if year < 2020 or year > 2030:
            return jsonify({'error': 'year must be between 2020 and 2030'}), 400
        
        nearby_schools = data.get('nearby_schools', '').lower() in ['true', '1', 'yes']
        nearby_metro = data.get('nearby_metro', '').lower() in ['true', '1', 'yes']
        commercial_area = data.get('commercial_area', '').lower() in ['true', '1', 'yes']
        area_type = data.get('area_type', 'residential')
        
        # Validate area_type
        valid_area_types = ['residential', 'commercial', 'agricultural', 'industrial']
        if area_type not in valid_area_types:
            return jsonify({
                'error': 'Invalid area_type',
                'valid_types': valid_area_types
            }), 400
        
        # Calculate estimate
        estimator = PriceEstimator()
        result = estimator.estimate_price(
            state=state,
            city_name=city,
            locality_name=locality,
            plot_size_sqft=plot_size,
            road_width_ft=road_width,
            nearby_schools=nearby_schools,
            nearby_metro=nearby_metro,
            commercial_area=commercial_area,
            year=year,
            area_type=area_type
        )
        
        # Save estimate to database
        estimate_record = PriceEstimate(
            state=state,
            city=city,
            locality=locality,
            plot_size_sqft=plot_size,
            road_width_ft=road_width,
            nearby_schools=nearby_schools,
            nearby_metro=nearby_metro,
            commercial_area=commercial_area,
            year=year,
            estimated_price_per_sqft=result['estimated_price_per_sqft'],
            total_estimated_price=result['total_estimated_price'],
            confidence_score=result['confidence_score'],
            api_key=g.api_key.key,
            ip_address=request.remote_addr
        )
        
        from app import db
        db.session.add(estimate_record)
        db.session.commit()
        
        # Update API key last used
        from datetime import datetime
        g.api_key.last_used = datetime.utcnow()
        db.session.commit()
        
        # Return result
        return jsonify({
            'success': True,
            'data': result,
            'metadata': {
                'api_version': '1.0',
                'timestamp': estimate_record.created_at.isoformat(),
                'estimate_id': estimate_record.id
            }
        })
        
    except Exception as e:
        logging.error(f"API Error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An error occurred while processing your request'
        }), 500

@api_bp.route('/cities', methods=['GET'])
@limiter.limit("100 per hour")
@require_api_key
def api_cities():
    """Get list of available cities"""
    from models import City
    
    state = request.args.get('state')
    
    query = City.query
    if state:
        query = query.filter_by(state=state)
    
    cities = query.order_by(City.name).all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': city.id,
            'name': city.name,
            'state': city.state,
            'tier': city.tier,
            'base_price_per_sqft': city.base_price_per_sqft
        } for city in cities]
    })

@api_bp.route('/localities', methods=['GET'])
@limiter.limit("100 per hour")
@require_api_key
def api_localities():
    """Get list of available localities"""
    from models import Locality, City
    
    city_name = request.args.get('city')
    state = request.args.get('state')
    
    if not city_name:
        return jsonify({'error': 'city parameter is required'}), 400
    
    # Find city
    city_query = City.query.filter_by(name=city_name)
    if state:
        city_query = city_query.filter_by(state=state)
    
    city = city_query.first()
    if not city:
        return jsonify({'error': 'City not found'}), 404
    
    localities = Locality.query.filter_by(city_id=city.id).order_by(Locality.name).all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': locality.id,
            'name': locality.name,
            'price_per_sqft': locality.price_per_sqft,
            'area_type': locality.area_type,
            'pin_code': locality.pin_code
        } for locality in localities]
    })

@api_bp.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Land Price Estimator API',
        'version': '1.0'
    })

@api_bp.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'You have exceeded the rate limit. Please try again later.'
    }), 429
