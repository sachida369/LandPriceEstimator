from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import csv
import logging
from models import User, City, Locality, InfrastructureMultiplier, APIKey, PriceEstimate
from data_manager import DataManager

auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username, is_admin=True).first()
        
        if user and user.check_password(password):
            session['admin_logged_in'] = True
            session['admin_user_id'] = user.id
            flash('Successfully logged in', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/dashboard')
@admin_required
def dashboard():
    from app import db
    
    # Get statistics
    total_cities = City.query.count()
    total_localities = Locality.query.count()
    total_estimates = PriceEstimate.query.count()
    total_api_keys = APIKey.query.filter_by(is_active=True).count()
    
    # Recent estimates
    recent_estimates = PriceEstimate.query.order_by(
        PriceEstimate.created_at.desc()
    ).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_cities=total_cities,
                         total_localities=total_localities,
                         total_estimates=total_estimates,
                         total_api_keys=total_api_keys,
                         recent_estimates=recent_estimates)

@auth_bp.route('/data-management')
@admin_required
def data_management():
    cities = City.query.order_by(City.name).all()
    multipliers = InfrastructureMultiplier.query.order_by(
        InfrastructureMultiplier.factor_type
    ).all()
    api_keys = APIKey.query.order_by(APIKey.created_at.desc()).all()
    
    return render_template('admin/data_management.html',
                         cities=cities,
                         multipliers=multipliers,
                         api_keys=api_keys)

@auth_bp.route('/upload-csv', methods=['POST'])
@admin_required
def upload_csv():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('auth.data_management'))
    
    file = request.files['file']
    data_type = request.form.get('data_type')
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('auth.data_management'))
    
    if file and file.filename.endswith('.csv'):
        try:
            # Save uploaded file temporarily
            file_path = os.path.join('uploads', file.filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(file_path)
            
            # Process the CSV
            data_manager = DataManager()
            
            if data_type == 'cities':
                success, message = data_manager.import_cities_csv(file_path)
            elif data_type == 'localities':
                success, message = data_manager.import_localities_csv(file_path)
            elif data_type == 'multipliers':
                success, message = data_manager.import_multipliers_csv(file_path)
            else:
                success, message = False, 'Invalid data type'
            
            # Clean up temporary file
            os.remove(file_path)
            
            if success:
                flash(message, 'success')
            else:
                flash(message, 'error')
                
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            logging.error(f"CSV upload error: {e}")
    else:
        flash('Please upload a CSV file', 'error')
    
    return redirect(url_for('auth.data_management'))

@auth_bp.route('/update-city', methods=['POST'])
@admin_required
def update_city():
    city_id = request.form.get('city_id')
    base_price = request.form.get('base_price')
    growth_rate = request.form.get('growth_rate')
    
    try:
        city = City.query.get(city_id)
        if city:
            city.base_price_per_sqft = float(base_price)
            city.growth_rate = float(growth_rate)
            
            from app import db
            db.session.commit()
            flash('City updated successfully', 'success')
        else:
            flash('City not found', 'error')
    except Exception as e:
        flash(f'Error updating city: {str(e)}', 'error')
        logging.error(f"City update error: {e}")
    
    return redirect(url_for('auth.data_management'))

@auth_bp.route('/create-api-key', methods=['POST'])
@admin_required
def create_api_key():
    name = request.form.get('name')
    rate_limit = int(request.form.get('rate_limit', 50))
    
    try:
        # Generate API key
        import secrets
        api_key = secrets.token_urlsafe(32)
        
        new_key = APIKey(
            key=api_key,
            name=name,
            rate_limit=rate_limit
        )
        
        from app import db
        db.session.add(new_key)
        db.session.commit()
        
        flash(f'API key created successfully: {api_key}', 'success')
    except Exception as e:
        flash(f'Error creating API key: {str(e)}', 'error')
        logging.error(f"API key creation error: {e}")
    
    return redirect(url_for('auth.data_management'))

@auth_bp.route('/toggle-api-key/<int:key_id>')
@admin_required
def toggle_api_key(key_id):
    try:
        api_key = APIKey.query.get(key_id)
        if api_key:
            api_key.is_active = not api_key.is_active
            
            from app import db
            db.session.commit()
            
            status = 'activated' if api_key.is_active else 'deactivated'
            flash(f'API key {status} successfully', 'success')
        else:
            flash('API key not found', 'error')
    except Exception as e:
        flash(f'Error updating API key: {str(e)}', 'error')
        logging.error(f"API key toggle error: {e}")
    
    return redirect(url_for('auth.data_management'))

@auth_bp.route('/export-data/<data_type>')
@admin_required
def export_data(data_type):
    """Export data as CSV"""
    try:
        data_manager = DataManager()
        
        if data_type == 'cities':
            csv_data = data_manager.export_cities_csv()
            filename = 'cities_export.csv'
        elif data_type == 'localities':
            csv_data = data_manager.export_localities_csv()
            filename = 'localities_export.csv'
        elif data_type == 'estimates':
            csv_data = data_manager.export_estimates_csv()
            filename = 'estimates_export.csv'
        else:
            flash('Invalid export type', 'error')
            return redirect(url_for('auth.data_management'))
        
        from flask import make_response
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        
        return response
        
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'error')
        logging.error(f"Data export error: {e}")
        return redirect(url_for('auth.data_management'))
