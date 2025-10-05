# 🏙️ Boston Daddy - Smart City Infrastructure Management Platform

> **HackHarvard 2025** - Comprehensive AI-powered city infrastructure management system for Boston's energy, traffic, and weather systems.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-19.1+-61dafb.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9+-3178c6.svg)](https://typescriptlang.org)

## 🎯 Project Overview

**Boston Daddy** is an intelligent city infrastructure management platform that addresses Boston's most pressing urban challenges through AI-powered insights and real-time monitoring. The platform integrates energy consumption, traffic patterns, and weather data to provide actionable recommendations for city officials and residents.

### 🏆 HackHarvard 2025 Track
- **Primary**: Aramco Power the Future

## 🚀 Key Features

### 🔋 **Energy Management System**
- **Real-time Building Analytics**: Monitor energy consumption across 15+ municipal buildings
- **Multi-fuel Tracking**: Electricity and solar energy usage monitoring
- **Cost Optimization**: AI-powered recommendations for energy efficiency improvements
- **Building Performance**: Energy intensity analysis and benchmarking
- **Predictive Analytics**: 48-hour energy demand forecasting

### 🚦 **Traffic Intelligence**
- **Real-time Traffic Monitoring**: 10+ intersection monitoring with directional flow analysis
- **Congestion Prediction**: AI-powered traffic pattern analysis and optimization
- **Weather-Traffic Integration**: Safety alerts for dangerous driving conditions
- **Cross-domain Correlation**: Traffic-energy usage correlation analysis
- **Dynamic Route Optimization**: Real-time traffic signal coordination

### 🌤️ **Weather Integration**
- **Real-time Weather Dashboard**: Current conditions and 24-hour forecasts
- **Climate Impact Analysis**: Weather-energy consumption correlation
- **Extreme Weather Alerts**: Automated safety notifications
- **Seasonal Optimization**: Weather-normalized energy usage analysis

### 🤖 **AI-Powered Insights**
- **Cross-domain Analysis**: Energy-traffic-weather correlation insights
- **Anomaly Detection**: Automated identification of unusual patterns
- **Cost Savings Opportunities**: Quantified recommendations for efficiency improvements
- **Gemini AI Integration**: Natural language city optimization suggestions
- **Predictive Maintenance**: Infrastructure issue prediction and prevention

## 🏗️ Architecture

### Backend (Python/Flask)
```
backend/
├── models/           # Data models (Energy, Traffic, Weather, Insights)
├── routes/           # API endpoints
├── services/         # Business logic and data generation
├── utils/            # Helper functions and database client
├── migrations/       # Database schema
└── config.py         # Configuration management
```

### Frontend (React/TypeScript)
```
frontend/
├── src/
│   ├── components/   # Reusable UI components
│   ├── features/     # Feature-specific components
│   ├── store/        # State management (Zustand)
│   ├── types/        # TypeScript type definitions
│   └── config/       # API configuration
```

### Database (Supabase/PostgreSQL)
- **Energy Buildings**: Municipal building data and energy readings
- **Traffic Data**: Intersection monitoring and vehicle flow data
- **Weather Stations**: Weather monitoring and historical data
- **Insights**: AI-generated recommendations and analysis

## 🛠️ Technology Stack

### Backend
- **Python 3.11+** with Flask framework
- **Supabase** for database and real-time features
- **Google Gemini AI** for natural language processing
- **Pandas/NumPy** for data analysis
- **Scikit-learn** for machine learning
- **SciPy** for statistical analysis

### Frontend
- **React 19.1+** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Shadcn/ui** for component library
- **Mapbox GL** for interactive maps
- **Zustand** for state management
- **TanStack Query** for data fetching

### Infrastructure
- **Supabase** for database and authentication
- **Mapbox** for mapping services
- **Google Cloud** for AI services

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- pnpm (recommended) or npm
- Supabase account
- Mapbox API key

### Backend Setup

1. **Clone and navigate to backend**
```bash
cd backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your Supabase credentials and API keys
```

4. **Run database migrations**
```bash
python run_migrations.py
```

5. **Start the Flask server**
```bash
python app.py
```

The backend will be available at `http://localhost:5001`

### Frontend Setup

1. **Navigate to frontend**
```bash
cd frontend
```

2. **Install dependencies**
```bash
pnpm install
```

3. **Configure environment**
```bash
cp .env.example .env.local
# Add your Mapbox token and API URLs
```

4. **Start the development server**
```bash
pnpm dev
```

The frontend will be available at `http://localhost:5173`

## 📊 Data Generation

The platform includes comprehensive data generation tools for demonstration:

### Generate All Data
```bash
# Backend API
POST http://localhost:5001/api/dashboard/generate-all-data

# Or use the frontend dashboard "Generate Data" button
```

### Individual Data Types
```bash
# Energy data
POST http://localhost:5001/api/energy/generate-data

# Traffic data  
POST http://localhost:5001/api/traffic/generate-data

# Weather data
POST http://localhost:5001/api/weather/generate-data

# AI insights
POST http://localhost:5001/api/insights/generate-insights
```

## 🎨 User Interface

### Dashboard Features
- **Overview Tab**: System statistics and energy map
- **Buildings Tab**: Detailed building analytics and energy readings
- **Map View**: Interactive 3D map with real-time traffic and building data
- **Weather Dashboard**: Real-time weather conditions and forecasts

### Key Components
- **Interactive Map**: 3D buildings with energy data overlays
- **Real-time Traffic**: Color-coded road visualization
- **AI Insights Panel**: Cross-domain recommendations
- **Building Details**: Comprehensive energy analytics

## 🔌 API Endpoints

### Energy Management
```
GET    /api/energy/buildings              # List all buildings
GET    /api/energy/buildings/{id}         # Building details
GET    /api/energy/buildings/{id}/readings # Energy readings
GET    /api/energy/dashboard-data         # Dashboard metrics
POST   /api/energy/generate-data          # Generate energy data
```

### Traffic Intelligence
```
GET    /api/traffic/intersections         # List intersections
GET    /api/traffic/data                  # Traffic data with filters
GET    /api/traffic/directional           # Directional traffic data
GET    /api/traffic/summary               # Traffic statistics
POST   /api/traffic/generate-data         # Generate traffic data
```

### Weather Integration
```
GET    /api/weather/stations              # Weather stations
GET    /api/weather/data                  # Weather data
GET    /api/weather/summary               # Weather summary
POST   /api/weather/generate-data         # Generate weather data
```

### AI Insights
```
GET    /api/insights/insights             # List insights
GET    /api/insights/building/{id}        # Building-specific insights
POST   /api/insights/generate-insights    # Generate AI insights
POST   /api/insights/suggestions          # City optimization suggestions
```

## 🧠 AI Features

### Cross-Domain Analysis
- **Energy-Traffic Correlation**: Identifies occupancy-driven consumption patterns
- **Weather-Energy Impact**: Quantifies weather dependency for buildings
- **Anomaly Detection**: Statistical analysis for unusual patterns
- **Predictive Analytics**: Future demand forecasting

### Gemini AI Integration
- **Natural Language Queries**: Ask questions about city infrastructure
- **Policy Explanation**: Complex decisions explained in plain language
- **City Optimization**: AI-generated actionable recommendations
- **Multi-language Support**: Accessibility for diverse populations

## 🎯 Real-World Impact

### Boston's Current Challenges Addressed
1. **Energy Grid Crisis**: 5 new substations needed by 2035
2. **Traffic Delays**: 8th globally for traffic delays
3. **Climate Adaptation**: Stormwater system capacity issues
4. **Infrastructure Aging**: Colonial-era systems need modernization

### Measurable Outcomes
- **13.5% Traffic Improvement**: Based on Google Project Green Light results
- **Energy Efficiency**: 15% reduction potential through optimization
- **Cost Savings**: Quantified recommendations for municipal budget
- **Climate Resilience**: Weather-adaptive infrastructure management

## 🔧 Configuration

### Environment Variables
```bash
# Backend (.env)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_api_key
WEATHER_API_KEY=your_weather_api_key

# Frontend (.env.local)
VITE_API_URL=http://localhost:5001
VITE_MAPBOX_TOKEN=your_mapbox_token
```

### Database Schema
The platform uses a comprehensive PostgreSQL schema with:
- **Energy tables**: Buildings and readings
- **Traffic tables**: Intersections and data
- **Weather tables**: Stations and data
- **Insights table**: AI-generated recommendations

## 🤝 Contributing

This project was developed for HackHarvard 2025. For contributions:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Team

**HackHarvard 2025 Team** - Boston Daddy
- Smart City Infrastructure Management
- AI-Powered Urban Analytics
- Cross-Domain Integration Platform

## 🔮 Future Enhancements

- **Regional Scaling**: Extension to entire Massachusetts metro area
- **Advanced Climate Modeling**: Sea level rise and extreme weather integration
- **Community Engagement**: Public participation in infrastructure planning
- **IoT Integration**: Real sensor data from city infrastructure
- **Mobile Application**: Citizen reporting and real-time updates

---

**Built with ❤️ for Boston's Smart City Future**