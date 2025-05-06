# Architecture Overview

## Overview

This repository contains an Environmental Monitoring System that collects, processes, and visualizes environmental data such as air quality (PM2.5, PM10), temperature, humidity, noise levels, and CO/CO2 concentrations. The project consists of a Flask-based backend server, a web interface, and a Flutter mobile application.

The system integrates with ThingsBoard IoT Platform for data collection and offers real-time monitoring capabilities through WebSocket connections. It also features a specialized Vietnamese Air Quality Index (VN_AQI) calculator that follows national standards.

## System Architecture

The system follows a client-server architecture with the following high-level components:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │  ThingsBoard    │
│  Web Interface  │◄────►│  Flask Backend  │◄────►│  IoT Platform   │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
         ▲                       ▲
         │                       │
         ▼                       ▼
┌─────────────────┐      ┌─────────────────┐
│                 │      │    VN_AQI       │
│ Flutter Mobile  │      │   Calculator    │
│   Application   │      │                 │
└─────────────────┘      └─────────────────┘
```

The system uses Socket.IO for real-time data transmission between the server and clients, and HTTP REST APIs for other interactions.

## Key Components

### Backend (Flask)

- **Core Server**: Implemented in `app.py`, provides the main HTTP server and API endpoints
- **SocketIO Integration**: Handles real-time updates using Flask-SocketIO
- **ThingsBoard Client**: Two implementations for ThingsBoard integration:
  - JWT-based REST client (`thingsboard_client.py`)
  - MQTT client (`thingsboard_mqtt_client.py`)
- **VN_AQI Calculator**: Implements Vietnamese AQI standards in `vn_aqi_calculator.py`
- **Server Runner**: `run.py` orchestrates the different components

### Web Frontend

- **HTML/CSS/JS**: Traditional web interface with responsive design
- **Templates**: Flask templates for server-side rendering
- **Progressive Web App (PWA)**: Includes service workers, manifest, and offline capabilities
- **Charts**: Client-side charting using Chart.js
- **Responsive Design**: Mobile-friendly interface with pull-to-refresh and other touch features

### Mobile Application (Flutter)

- **Cross-platform**: Flutter application with Android/iOS/web support
- **State Management**: Uses provider package for state management
- **UI Components**: Custom widgets for parameter cards, charts, and status indicators
- **HTTP Client**: Integration with the backend APIs
- **Charts**: Uses fl_chart for data visualization

### Data Flow

The system collects data from environmental sensors via ThingsBoard, processes it in the backend, and delivers it to the clients:

1. Environmental sensors send data to ThingsBoard IoT platform
2. The Flask backend regularly pulls data from ThingsBoard using JWT authentication
3. The VN_AQI calculator processes raw data to calculate air quality indices
4. Data is stored temporarily in memory
5. Real-time updates are pushed to connected clients via Socket.IO
6. Clients (web and mobile) visualize the data and provide user notifications

## External Dependencies

### Backend Dependencies

- **Flask**: Web framework
- **Flask-SocketIO**: WebSocket implementation
- **Eventlet**: Asynchronous networking library
- **Requests**: HTTP client
- **Paho-MQTT**: MQTT client for IoT communication
- **Colorama**: Terminal coloring for console output

### Frontend Dependencies

- **Chart.js**: JavaScript charting library
- **Font Awesome**: Icon library

### Mobile Dependencies

- **Flutter**: UI toolkit
- **HTTP/Dio**: Networking libraries
- **fl_chart**: Charting library
- **Provider**: State management
- **Flutter SVG**: SVG rendering

### External Services

- **ThingsBoard**: IoT platform for collecting, processing, and visualizing IoT device data
  - Uses both REST API and MQTT protocols
  - Secured with JWT authentication

## Authentication & Security

- JWT-based authentication for ThingsBoard API access
- Access tokens for device communication
- Environment variables for sensitive configuration

## Deployment Strategy

The repository includes configuration for deployment in a Replit environment:

- **Workflows**: Defined in `.replit` for running components
- **Port Configuration**: Exposes port 5000 for the web interface
- **Environment Variables**: Uses environment variables for sensitive data
- **Progressive Web App**: Support for installing the web interface as a PWA
- **Service Workers**: Enables offline functionality for the web interface

Additionally, the Flutter application is structured for deployment to:
- Web (as a PWA)
- Android
- iOS
- macOS
- Windows
- Linux

## Data Storage

The current implementation primarily uses in-memory storage with some features:

- **Temporary Caching**: Data is cached in memory to reduce API calls to ThingsBoard
- **Fallback Mechanism**: If ThingsBoard is unavailable, the system uses cached or simulated data
- **Historical Data**: Limited historical data is maintained in memory

## Future Considerations

1. **Persistent Storage**: Implementing a database for long-term data storage and analytics
2. **User Authentication**: Adding user accounts and authentication for the web and mobile apps
3. **Additional Sensors**: Support for more environmental parameters and sensor types
4. **Analytics**: Advanced data analysis and prediction capabilities
5. **Notifications**: Enhanced push notification system for alerts