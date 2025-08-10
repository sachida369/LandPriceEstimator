from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from models import City, Locality, PriceEstimate
from price_estimator import PriceEstimator
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    cities = City.query.order_by(City.name).all()
    return render_template('index.html', cities=cities)

@main_bp.route('/estimate', methods=['GET', 'POST'])
def estimate():
    if request.method == 'POST':
        try:
            # Get form data
            state = request.form.get('state')
            city = request.form.get('city')
            locality = request.form.get('locality')
            plot_size = float(request.form.get('plot_size', 1000))
            road_width = float(request.form.get('road_width', 20))
            nearby_schools = 'nearby_schools' in request.form
            nearby_metro = 'nearby_metro' in request.form
            commercial_area = 'commercial_area' in request.form
            year = int(request.form.get('year', 2024))
            area_type = request.form.get('area_type', 'residential')
            
            # Validate inputs
            if not state or not city:
                flash('State and City are required fields', 'error')
                return redirect(url_for('main.index'))
            
            if plot_size <= 0:
                flash('Plot size must be greater than 0', 'error')
                return redirect(url_for('main.index'))
            
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
                ip_address=request.remote_addr
            )
            
            from app import db
            db.session.add(estimate_record)
            db.session.commit()
            
            # Format prices for display
            result['formatted_price_per_sqft'] = format_indian_currency(result['estimated_price_per_sqft'])
            result['formatted_total_price'] = format_indian_currency(result['total_estimated_price'])
            
            # Store in session for recent searches
            if 'recent_searches' not in session:
                session['recent_searches'] = []
            
            search_data = {
                'state': state,
                'city': city,
                'locality': locality,
                'plot_size': plot_size,
                'total_price': result['formatted_total_price'],
                'timestamp': estimate_record.created_at.strftime('%Y-%m-%d %H:%M')
            }
            
            session['recent_searches'].insert(0, search_data)
            session['recent_searches'] = session['recent_searches'][:5]  # Keep only last 5
            session.modified = True
            
            return render_template('estimate.html', 
                                 result=result, 
                                 input_data={
                                     'state': state,
                                     'city': city,
                                     'locality': locality,
                                     'plot_size': plot_size,
                                     'road_width': road_width,
                                     'nearby_schools': nearby_schools,
                                     'nearby_metro': nearby_metro,
                                     'commercial_area': commercial_area,
                                     'year': year,
                                     'area_type': area_type
                                 })
            
        except ValueError as e:
            flash('Invalid input values. Please check your entries.', 'error')
            logging.error(f"ValueError in estimate: {e}")
            return redirect(url_for('main.index'))
        except Exception as e:
            flash('An error occurred while calculating the estimate. Please try again.', 'error')
            logging.error(f"Error in estimate: {e}")
            return redirect(url_for('main.index'))
    
    return redirect(url_for('main.index'))

@main_bp.route('/api/localities/<int:city_id>')
def get_localities(city_id):
    """API endpoint to get localities for a city"""
    localities = Locality.query.filter_by(city_id=city_id).order_by(Locality.name).all()
    return jsonify([{
        'id': locality.id,
        'name': locality.name
    } for locality in localities])

@main_bp.route('/recent-searches')
def recent_searches():
    """Get recent searches from session"""
    return jsonify(session.get('recent_searches', []))

def format_indian_currency(amount):
    """Format amount in Indian currency with commas"""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.2f}"
