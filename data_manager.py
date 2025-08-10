import csv
import io
import logging
from models import City, Locality, InfrastructureMultiplier, PriceEstimate
from app import db

class DataManager:
    def __init__(self):
        pass
    
    def import_cities_csv(self, file_path):
        """Import cities from CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                updated_count = 0
                created_count = 0
                
                for row in csv_reader:
                    city = City.query.filter_by(
                        name=row['name'], 
                        state=row['state']
                    ).first()
                    
                    if city:
                        # Update existing city
                        city.base_price_per_sqft = float(row['base_price_per_sqft'])
                        city.growth_rate = float(row.get('growth_rate', 0.05))
                        city.population = int(row.get('population', 0)) if row.get('population') else None
                        city.tier = row.get('tier')
                        updated_count += 1
                    else:
                        # Create new city
                        city = City(
                            name=row['name'],
                            state=row['state'],
                            base_price_per_sqft=float(row['base_price_per_sqft']),
                            growth_rate=float(row.get('growth_rate', 0.05)),
                            population=int(row.get('population', 0)) if row.get('population') else None,
                            tier=row.get('tier')
                        )
                        db.session.add(city)
                        created_count += 1
                
                db.session.commit()
                return True, f"Successfully imported {created_count} new cities and updated {updated_count} existing cities"
                
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error importing cities CSV: {e}")
            return False, f"Error importing cities: {str(e)}"
    
    def import_localities_csv(self, file_path):
        """Import localities from CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                updated_count = 0
                created_count = 0
                
                for row in csv_reader:
                    # Find the city
                    city = City.query.filter_by(
                        name=row['city_name'], 
                        state=row['state']
                    ).first()
                    
                    if not city:
                        logging.warning(f"City not found: {row['city_name']}, {row['state']}")
                        continue
                    
                    locality = Locality.query.filter_by(
                        name=row['name'], 
                        city_id=city.id
                    ).first()
                    
                    if locality:
                        # Update existing locality
                        locality.price_per_sqft = float(row['price_per_sqft'])
                        locality.location_multiplier = float(row.get('location_multiplier', 1.0))
                        locality.area_type = row.get('area_type', 'residential')
                        locality.pin_code = row.get('pin_code')
                        updated_count += 1
                    else:
                        # Create new locality
                        locality = Locality(
                            name=row['name'],
                            city_id=city.id,
                            price_per_sqft=float(row['price_per_sqft']),
                            location_multiplier=float(row.get('location_multiplier', 1.0)),
                            area_type=row.get('area_type', 'residential'),
                            pin_code=row.get('pin_code')
                        )
                        db.session.add(locality)
                        created_count += 1
                
                db.session.commit()
                return True, f"Successfully imported {created_count} new localities and updated {updated_count} existing localities"
                
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error importing localities CSV: {e}")
            return False, f"Error importing localities: {str(e)}"
    
    def import_multipliers_csv(self, file_path):
        """Import infrastructure multipliers from CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                updated_count = 0
                created_count = 0
                
                for row in csv_reader:
                    multiplier = InfrastructureMultiplier.query.filter_by(
                        factor_type=row['factor_type'],
                        factor_value=row['factor_value']
                    ).first()
                    
                    if multiplier:
                        # Update existing multiplier
                        multiplier.multiplier = float(row['multiplier'])
                        multiplier.description = row.get('description', '')
                        updated_count += 1
                    else:
                        # Create new multiplier
                        multiplier = InfrastructureMultiplier(
                            factor_type=row['factor_type'],
                            factor_value=row['factor_value'],
                            multiplier=float(row['multiplier']),
                            description=row.get('description', '')
                        )
                        db.session.add(multiplier)
                        created_count += 1
                
                db.session.commit()
                return True, f"Successfully imported {created_count} new multipliers and updated {updated_count} existing multipliers"
                
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error importing multipliers CSV: {e}")
            return False, f"Error importing multipliers: {str(e)}"
    
    def export_cities_csv(self):
        """Export cities to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['name', 'state', 'base_price_per_sqft', 'growth_rate', 'population', 'tier'])
        
        # Write data
        cities = City.query.order_by(City.state, City.name).all()
        for city in cities:
            writer.writerow([
                city.name,
                city.state,
                city.base_price_per_sqft,
                city.growth_rate,
                city.population or '',
                city.tier or ''
            ])
        
        return output.getvalue()
    
    def export_localities_csv(self):
        """Export localities to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['name', 'city_name', 'state', 'price_per_sqft', 'location_multiplier', 'area_type', 'pin_code'])
        
        # Write data
        localities = db.session.query(Locality, City).join(City).order_by(City.state, City.name, Locality.name).all()
        for locality, city in localities:
            writer.writerow([
                locality.name,
                city.name,
                city.state,
                locality.price_per_sqft,
                locality.location_multiplier,
                locality.area_type or '',
                locality.pin_code or ''
            ])
        
        return output.getvalue()
    
    def export_estimates_csv(self):
        """Export price estimates to CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'id', 'state', 'city', 'locality', 'plot_size_sqft', 'road_width_ft',
            'nearby_schools', 'nearby_metro', 'commercial_area', 'year',
            'estimated_price_per_sqft', 'total_estimated_price', 'confidence_score',
            'api_key', 'ip_address', 'created_at'
        ])
        
        # Write data
        estimates = PriceEstimate.query.order_by(PriceEstimate.created_at.desc()).all()
        for estimate in estimates:
            writer.writerow([
                estimate.id,
                estimate.state,
                estimate.city,
                estimate.locality or '',
                estimate.plot_size_sqft,
                estimate.road_width_ft,
                estimate.nearby_schools,
                estimate.nearby_metro,
                estimate.commercial_area,
                estimate.year,
                estimate.estimated_price_per_sqft,
                estimate.total_estimated_price,
                estimate.confidence_score,
                estimate.api_key or '',
                estimate.ip_address or '',
                estimate.created_at.isoformat()
            ])
        
        return output.getvalue()
