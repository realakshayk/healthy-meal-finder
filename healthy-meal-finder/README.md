# Healthy Meal Finder API

A comprehensive FastAPI application for finding healthy meal recommendations based on location and fitness goals. Built with clean architecture principles and optimized for partner consumption with consistent response formatting and API versioning.

## Features

- **Location-based search**: Find restaurants near your location
- **Fitness goal matching**: Get meals tailored to your fitness goals
- **Natural language input**: Accept user-friendly terms like "musle gain" or "lean bulk"
- **Fuzzy string matching**: Handle misspellings and synonyms automatically
- **AI-powered nutrition estimation**: OpenAI-based nutrition analysis from meal descriptions
- **Nutritional analysis**: Detailed nutritional information for each meal
- **Smart scoring**: Meals are scored based on how well they match your goals
- **Partner-friendly API**: Clean response formatting with consistent structure
- **API versioning**: All endpoints under `/api/v1/` for easy versioning
- **Comprehensive documentation**: Full OpenAPI/Swagger documentation
- **Health checks**: Built-in health and readiness endpoints

## Supported Fitness Goals

- **Muscle Gain**: High protein, moderate calories for muscle building
- **Weight Loss**: Lower calories, moderate protein for weight loss
- **Keto**: Low carbs, high fat for ketosis
- **Balanced**: General healthy eating guidelines

## API Structure

The project follows clean architecture principles with clear separation of concerns:

```
healthy-meal-finder/
├── main.py                    # FastAPI application entry point
├── api/                      # API versioning structure
│   └── v1/                  # API version 1
│       ├── endpoints/       # API route handlers
│       │   ├── meals.py    # Meal-related endpoints
│       │   └── health.py   # Health check endpoints
│       └── router.py       # Main v1 API router
├── schemas/                 # Pydantic models for request/response
│   ├── requests.py         # Request models
│   └── responses.py        # Response models with ApiResponse wrapper
├── services/               # Business logic layer
│   └── meal_service.py     # Meal service with Google Places integration
├── core/                   # Shared functionality
│   └── dependencies.py     # Dependency injection utilities
├── fitness_goals.py        # Nutrition rules for different goals
├── meal_utils.py           # Meal scoring utilities
├── menu_generator.py       # Mock menu generation
├── mock_meals.py           # Mock meal data
└── requirements.txt        # Python dependencies
```

## API Endpoints

All endpoints are versioned under `/api/v1/` and return consistent response formatting:

### Core Endpoints

#### `POST /api/v1/meals/find`
Find healthy meal recommendations based on location and fitness goals.

**Request Body:**
```json
{
  "lat": 40.7128,
  "lon": -74.0060,
  "goal": "musle gain",
  "radius_miles": 5.0,
  "max_results": 10
}
```

**Note**: The `goal` field accepts natural language input. Examples:
- `"musle gain"`, `"lean bulk"`, `"bulking"` → muscle_gain
- `"lose weight"`, `"fat loss"`, `"cutting"` → weight_loss  
- `"keto"`, `"low carb"`, `"ketogenic"` → keto
- `"balanced"`, `"healthy eating"`, `"maintenance"` → balanced

**Response:**
```json
{
  "success": true,
  "data": {
    "meals": [
      {
        "restaurant": "Sweetgreen - SoHo",
        "dish": "Chicken + Brussels Bowl",
        "description": "Grilled chicken with roasted Brussels sprouts",
        "nutrition": {
          "calories": 485,
          "protein": 34,
          "carbs": 29,
          "fat": 21
        },
        "distance_miles": 1.2,
        "score": 3,
        "goal_match": "muscle_gain",
        "restaurant_info": {
          "name": "Sweetgreen - SoHo",
          "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
          "address": "123 Main St, New York, NY",
          "rating": 4.5,
          "user_ratings_total": 1250,
          "location": {"lat": 40.7128, "lng": -74.0060},
          "types": ["restaurant", "food", "establishment"],
          "distance_miles": 1.2
        }
      }
    ],
    "total_found": 25,
    "search_radius": 5.0,
    "goal": "muscle_gain"
  },
  "message": "Meals found successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "api_version": "v1"
}
```

#### `GET /api/v1/meals/goals`
Get available fitness goals and their descriptions.

**Response:**
```json
{
  "success": true,
  "data": {
    "goals": [
      {
        "id": "muscle_gain",
        "name": "Muscle Gain",
        "description": "High protein, moderate calories for muscle building",
        "nutrition_focus": ["high_protein", "moderate_calories"]
      }
    ]
  },
  "message": "Fitness goals retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "api_version": "v1"
}
```

#### `GET /api/v1/meals/nutrition-rules/{goal}`
Get detailed nutrition rules for a specific fitness goal.

**Response:**
```json
{
  "success": true,
  "data": {
    "goal": "muscle_gain",
    "rules": {
      "min_protein": 25,
      "max_calories": 800,
      "max_carbs": 60
    },
    "description": "High protein, moderate calories for muscle building"
  },
  "message": "Nutrition rules retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "api_version": "v1"
}
```

#### `GET /api/v1/meals/match-goal/{user_input}`
Test fuzzy matching for a user input string.

**Response:**
```json
{
  "success": true,
  "data": {
    "user_input": "musle gain",
    "matched_goal": "muscle_gain",
    "confidence": 95,
    "goal_name": "Muscle Gain",
    "suggestions": [
      {"goal_id": "weight_loss", "name": "Weight Loss", "score": 45},
      {"goal_id": "keto", "name": "Ketogenic Diet", "score": 30}
    ]
  },
  "message": "Goal matched successfully",
  "timestamp": "2024-0-15T10:30:00Z",
  "api_version": "v1"
}
```

### Nutrition Estimation Endpoints

#### `POST /api/v1/nutrition/estimate`
Estimate nutrition from a meal description using AI.

**Request Body:**
```json
{
  "meal_description": "Grilled chicken breast with quinoa and roasted vegetables",
  "serving_size": "1 serving"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "meal_description": "Grilled chicken breast with quinoa and roasted vegetables",
    "serving_size": "1 serving",
    "nutrition": {
      "calories": 485,
      "protein": 34,
      "carbs": 29,
      "fat": 21
    },
    "validation": {
      "is_valid": true,
      "message": "Valid nutrition estimate"
    },
    "estimation_method": "openai"
  },
  "message": "Nutrition estimated successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "api_version": "v1"
}
```

#### `POST /api/v1/nutrition/estimate-batch`
Estimate nutrition for multiple meals in batch.

**Request Body:**
```json
[
  {
    "meal_description": "Grilled chicken breast with quinoa",
    "serving_size": "1 serving"
  },
  {
    "meal_description": "Caesar salad with grilled salmon",
    "serving_size": "1 large bowl"
  }
]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "meals": [
      {
        "meal_description": "Grilled chicken breast with quinoa",
        "serving_size": "1 serving",
        "nutrition": {
          "calories": 485,
          "protein": 34,
          "carbs": 29,
          "fat": 21
        }
      },
      {
        "meal_description": "Caesar salad with grilled salmon",
        "serving_size": "1 large bowl",
        "nutrition": {
          "calories": 320,
          "protein": 28,
          "carbs": 15,
          "fat": 18
        }
      }
    ],
    "estimation_method": "openai",
    "total_meals": 2
  },
  "message": "Batch nutrition estimation completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "api_version": "v1"
}
```

#### `GET /api/v1/nutrition/validate/{calories}/{protein}/{carbs}/{fat}`
Validate a nutrition estimate for reasonableness.

**Response:**
```json
{
  "success": true,
  "data": {
    "nutrition": {
      "calories": 485,
      "protein": 34,
      "carbs": 29,
      "fat": 21
    },
    "validation": {
      "is_valid": true,
      "message": "Valid nutrition estimate"
    },
    "calculated_calories": 485
  },
  "message": "Nutrition validation completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "api_version": "v1"
}
```

### Health Endpoints

#### `GET /api/v1/health/`
Check the health status of the API.

#### `GET /api/v1/health/ready`
Check if the service is ready to handle requests.

#### `GET /api/v1/health/status`
Get detailed status information about the API service.

#### `GET /`
Root endpoint with API information and available endpoints.

## Response Format

All API responses follow a consistent format for easy partner consumption:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z",
  "api_version": "v1"
}
```

**Response Fields:**
- `success`: Boolean indicating if the request was successful
- `data`: The actual response data (optional for errors)
- `message`: Human-readable message about the operation
- `error`: Error message if success is false (optional)
- `detail`: Detailed error information (optional)
- `status_code`: HTTP status code (optional)
- `timestamp`: ISO timestamp of the response
- `api_version`: API version used

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd healthy-meal-finder
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional)**
   ```bash
   # Create a .env file for Google Maps API key
   echo "GOOGLE_MAPS_API_KEY=your_api_key_here" > .env
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/openapi.json

## Testing

### Basic Testing
Run the basic test script to verify all endpoints:

```bash
python test_api.py
```

### Partner Testing
Run the comprehensive partner test script:

```bash
python test_partner_api.py
```

This script tests:
- All API endpoints
- Response format consistency
- Error handling
- Different meal search scenarios
- Health and status endpoints

### Fuzzy Matching Testing
Test the natural language matching functionality:

```bash
python test_fuzzy_matching.py
```

This script tests:
- Various user input variations
- Misspellings and synonyms
- Confidence scoring
- Error handling for invalid inputs
- Integration with meal search

### Nutrition Estimation Testing
Test the AI-powered nutrition estimation functionality:

```bash
python test_nutrition_estimation.py
```

This script tests:
- Single meal nutrition estimation
- Batch nutrition estimation
- Nutrition validation
- Error handling for invalid inputs
- Different estimation methods (OpenAI vs fallback)
- Various meal types and serving sizes

## Configuration

### Environment Variables

- `GOOGLE_MAPS_API_KEY`: Google Maps API key for restaurant discovery (optional)
- `OPENAI_API_KEY`: OpenAI API key for nutrition estimation (optional)
- `ENVIRONMENT`: Environment name (development/production)
- `DEBUG`: Enable debug mode (true/false)

### Google Maps API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Places API
4. Create credentials (API key)
5. Add the API key to your `.env` file

**Note**: If no Google Maps API key is provided, the service will use mock restaurant data. If no OpenAI API key is provided, nutrition estimation will use a fallback keyword-based method.

## Partner Integration

### Authentication
The API is designed for partner consumption with future authentication support:

```python
import requests

# Example partner integration with natural language input
response = requests.post(
    "https://api.healthymealfinder.com/api/v1/meals/find",
    json={
        "lat": 40.7128,
        "lon": -74.0060,
        "goal": "musle gain",  # Natural language input
        "radius_miles": 5.0,
        "max_results": 10
    },
    headers={
        "Authorization": "Bearer your_api_key",
        "X-Partner-ID": "your_partner_id"
    }
)

if response.status_code == 200:
    data = response.json()
    if data["success"]:
        meals = data["data"]["meals"]
        # Process meal recommendations
        print(f"Matched goal: {data['data']['goal']}")
        print(f"Message: {data['message']}")  # May include confidence info
    else:
        print(f"Error: {data.get('error')}")
```

### Natural Language Input Examples

The API accepts various natural language inputs for fitness goals:

```python
# Muscle gain variations
"musle gain", "lean bulk", "bulking", "muscle building", "gain muscle"

# Weight loss variations  
"lose weight", "fat loss", "cutting", "slim down", "burn fat"

# Keto variations
"keto", "ketogenic", "low carb", "keto diet", "ketosis"

# Balanced variations
"balanced", "healthy eating", "maintenance", "wellness"

### Nutrition Estimation Examples

The API can estimate nutrition from natural language meal descriptions:

```python
# Single meal estimation
response = requests.post(
    "https://api.healthymealfinder.com/api/v1/nutrition/estimate",
    json={
        "meal_description": "Grilled chicken breast with quinoa and roasted vegetables",
        "serving_size": "1 serving"
    }
)

# Batch estimation
response = requests.post(
    "https://api.healthymealfinder.com/api/v1/nutrition/estimate-batch",
    json=[
        {"meal_description": "Grilled chicken breast with quinoa", "serving_size": "1 serving"},
        {"meal_description": "Caesar salad with grilled salmon", "serving_size": "1 large bowl"}
    ]
)

# Nutrition validation
response = requests.get(
    "https://api.healthymealfinder.com/api/v1/nutrition/validate/485/34/29/21"
)
```

**Features:**
- AI-powered estimation using OpenAI GPT models
- Fallback keyword-based estimation when OpenAI unavailable
- Validation of nutrition estimates for reasonableness
- Support for various meal descriptions and serving sizes
- Batch processing for multiple meals

### Rate Limiting
The API includes rate limiting support for partner applications:
- 100 requests per minute
- 1000 requests per hour
- Configurable per partner

### Error Handling
All errors return consistent formatting:

```json
{
  "success": false,
  "error": "Invalid fitness goal provided",
  "detail": "Goal must be one of: muscle_gain, weight_loss, keto, balanced",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00Z",
  "api_version": "v1"
}
```

## Authentication

All partner-facing endpoints require an API key via the `X-API-Key` header.

- Example header:
  `X-API-Key: testkey123`
- Allowed keys are set via the `ALLOWED_API_KEYS` environment variable (comma-separated).
- Health endpoints do not require authentication.

**Example usage:**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/meals/find",
    headers={"X-API-Key": "testkey123"},
    json={
        "lat": 40.7128,
        "lon": -74.0060,
        "goal": "musle gain",
        "radius_miles": 5.0,
        "max_results": 10
    }
)

if response.status_code == 200:
    print(response.json())
else:
    print("Error:", response.status_code, response.text)
```

## Development

### Project Structure

The project follows clean architecture principles:

- **API Layer**: Versioned endpoints under `/api/v1/`
- **Services**: Business logic and external integrations
- **Schemas**: Request/response models with validation
- **Core**: Shared utilities and dependencies

### Adding New Endpoints

1. Create a new endpoint file in `api/v1/endpoints/`
2. Define request/response schemas in `schemas/`
3. Implement business logic in `services/`
4. Include the endpoint in `api/v1/router.py`

### Adding New API Versions

1. Create a new version directory: `api/v2/`
2. Copy and modify the v1 structure
3. Update the main router to include the new version
4. Update version dependencies in `core/dependencies.py`

## Deployment

### Production Considerations

1. **Environment Variables**: Configure all sensitive data via environment variables
2. **CORS**: Update CORS settings for your domain
3. **Rate Limiting**: Configure rate limiting per partner
4. **Authentication**: Implement proper API key validation
5. **Monitoring**: Add health checks and monitoring
6. **Logging**: Configure structured logging
7. **SSL**: Use HTTPS in production

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: healthy-meal-finder
spec:
  replicas: 3
  selector:
    matchLabels:
      app: healthy-meal-finder
  template:
    metadata:
      labels:
        app: healthy-meal-finder
    spec:
      containers:
      - name: api
        image: healthymealfinder:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_MAPS_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: google-maps-api-key
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For support, please contact: support@healthymealfinder.com
