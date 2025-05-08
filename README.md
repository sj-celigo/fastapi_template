# FastAPI Template

A robust FastAPI template project with security and essential modules for building production-ready REST APIs.

## Features

- 🚀 Modern FastAPI framework
- 🔒 JWT Authentication with role-based access control
- 📝 Pydantic data validation
- 🧪 Testing suite with pytest
- 🔍 OpenAPI documentation
- 🛡️ Security features (CORS, rate limiting, security headers)
- 🎯 Health check endpoints
- 📈 Logging with loguru
- 🔄 Docker and docker-compose for development and deployment
- 📦 Environment variable configuration

## Project Structure

```
fastapi_template/
├── app/
│   ├── api/                 # Route definitions
│   ├── core/                # App settings, security, logging
│   ├── models/              # Pydantic schemas and models
│   ├── services/            # Business logic
│   ├── auth/                # Authentication logic (JWT/OAuth)
│   ├── middlewares/         # Custom middlewares
│   └── main.py              # Entry point
├── tests/                   # Unit and integration tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Docker and docker-compose (optional but recommended)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fastapi_template.git
   cd fastapi_template
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy the example env file and modify as needed:
   ```bash
   cp env.example .env
   ```

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Navigate to `http://localhost:8000/docs` to see the API documentation.

### Docker Development

1. Start the service with docker-compose:
   ```bash
   docker-compose up -d
   ```

2. The API will be available at `http://localhost:8000`

## Testing

Run tests:
```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation 