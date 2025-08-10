# Land Price Estimator - India

A comprehensive web application and REST API for estimating land prices across India. Built with Flask, featuring real estate data from 50+ cities and 200+ localities, with infrastructure-based pricing models and admin management capabilities.

## 🚀 Features

### Core Functionality
- **Price Estimation API**: RESTful API for land price calculations
- **Web Interface**: User-friendly form-based estimation tool
- **Multi-language Support**: English and Hindi UI labels
- **Mobile Responsive**: Optimized for real estate professionals on-the-go
- **PDF Reports**: Downloadable estimation reports with detailed breakdowns

### Advanced Features
- **Smart Pricing Algorithm**: Considers location, infrastructure, and market trends
- **Fallback Mechanism**: State/regional averages when locality data unavailable
- **Infrastructure Analysis**: Road width, metro, schools, commercial proximity factors
- **Area Type Support**: Residential, commercial, agricultural, industrial calculations
- **Year Trend Analysis**: Historical and projected price adjustments

### Admin Management
- **Secure Admin Panel**: Data management and system monitoring
- **CSV Data Import/Export**: Bulk update capabilities for cities, localities, and multipliers
- **API Key Management**: Generate and manage external API access
- **Real-time Analytics**: Dashboard with usage statistics and recent estimates

## 🏗️ Architecture

### Backend
- **Flask**: Python web framework with SQLAlchemy ORM
- **SQLite**: Lightweight database for data storage
- **Rate Limiting**: 50 requests/hour for free tier API access
- **CORS Support**: Cross-origin requests enabled
- **Input Validation**: Comprehensive parameter validation and error handling

### Frontend
- **Bootstrap 5**: Responsive UI framework with dark theme
- **Vanilla JavaScript**: Form interactions and API calls
- **Chart.js**: Data visualization for admin dashboard
- **jsPDF**: Client-side PDF generation

### Data Processing
- **Pandas**: CSV data processing and validation
- **Scikit-learn**: Basic regression models for price estimation
- **Government Data Ready**: Structured to parse official real estate data

## 📊 Data Sources

### Included Datasets
- **50+ Cities**: Major Indian cities with base prices and growth rates
- **200+ Localities**: Neighborhood-level pricing for metro areas
- **Infrastructure Multipliers**: 40+ factors affecting land values
- **Tier Classifications**: City categorization (Tier 1, 2, 3) with population data

### Data Structure
