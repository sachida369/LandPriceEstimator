# Land Price Estimator - India

## Overview

A comprehensive web application and REST API for estimating land prices across India. The system combines a Flask backend with a responsive web interface to provide accurate property valuations based on location, infrastructure factors, and market trends. Features real estate data from 50+ cities and 200+ localities with infrastructure-based pricing algorithms, fallback mechanisms, and multi-language support.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Flask Framework**: Core web application using SQLAlchemy ORM for database operations
- **SQLite Database**: Lightweight storage for cities, localities, users, API keys, and price estimates
- **Modular Blueprint Structure**: Separate blueprints for main routes (`routes.py`), API endpoints (`api.py`), and admin authentication (`auth.py`)
- **Price Estimation Engine**: Custom `PriceEstimator` class implementing weighted scoring algorithm considering location multipliers, infrastructure factors, and year trends
- **Fallback Mechanism**: State/regional averages used when specific locality data is unavailable

### Database Design
- **Core Entities**: Users (admin authentication), Cities (base prices and growth rates), Localities (specific area pricing), Infrastructure Multipliers (road width, metro, schools factors)
- **Relationships**: Cities contain multiple localities with foreign key relationships
- **Audit Trail**: Price estimates logged with timestamps and input parameters

### API Architecture
- **RESTful Design**: `/api/estimate` endpoint supporting both POST and GET methods
- **Authentication**: API key-based authentication with database-stored keys
- **Rate Limiting**: 50 requests per hour using Flask-Limiter
- **CORS Support**: Cross-origin requests enabled for external integrations
- **Input Validation**: Comprehensive parameter validation with error handling

### Frontend Architecture
- **Server-Side Rendering**: Jinja2 templates with Bootstrap 5 for responsive design
- **Progressive Enhancement**: Vanilla JavaScript for form interactions and API calls
- **Dark Theme**: Bootstrap dark theme with custom CSS enhancements
- **Mobile-First**: Responsive design optimized for real estate professionals
- **Client-Side PDF Generation**: jsPDF for downloadable estimation reports

### Authentication & Authorization
- **Session-Based Admin Auth**: Secure admin panel with password hashing using Werkzeug
- **API Key Management**: Generate and manage external API access tokens
- **Role-Based Access**: Admin-only access to data management and system monitoring

### Data Management System
- **CSV Import/Export**: Bulk update capabilities through `DataManager` class
- **Seed Data**: Initial dataset with major Indian cities and pricing data
- **Manual Override**: Admin interface for real-time data updates
- **Validation Layer**: Data integrity checks during import operations

### Price Calculation Algorithm
The system uses a multi-factor weighted scoring approach:
1. **Base Price**: City or locality-specific price per square foot from database
2. **Location Multiplier**: Demand-based adjustment for specific areas
3. **Infrastructure Multiplier**: Calculated based on road width, metro proximity, schools, commercial areas
4. **Year Trend Factor**: Inflation and market trend adjustments using configurable growth rates
5. **Area Type Factor**: Residential, commercial, agricultural, industrial multipliers
6. **Confidence Scoring**: Data availability and accuracy indicators

## External Dependencies

### Backend Dependencies
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **Flask-CORS**: Cross-origin resource sharing support
- **Flask-Limiter**: API rate limiting functionality
- **Werkzeug**: Security utilities for password hashing
- **Pandas**: CSV data processing and validation
- **Scikit-learn**: Basic regression models for price estimation

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme support
- **Font Awesome**: Icon library for enhanced UX
- **Chart.js**: Data visualization for admin dashboard
- **jsPDF**: Client-side PDF report generation

### Development & Testing
- **Unittest**: Python testing framework for API and estimation logic
- **Mock Data**: Test fixtures for cities, localities, and infrastructure factors

### Deployment Considerations
- **Environment Variables**: Configuration through `config.py` with fallback defaults
- **SQLite**: Production-ready for small to medium scale deployments
- **Static File Serving**: Flask serves CSS, JS, and other assets
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

The system is designed to be self-contained with minimal external dependencies, making it suitable for deployment on platforms like Replit while maintaining production-ready capabilities.