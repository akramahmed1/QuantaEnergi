"""
Swagger UI Setup for QuantaEnergi API
This script sets up Swagger UI integration with the FastAPI application
"""

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import yaml
import json
from pathlib import Path

def setup_swagger_ui(app: FastAPI, openapi_file_path: str = "openapi.yaml"):
    """
    Set up Swagger UI for the FastAPI application
    
    Args:
        app: FastAPI application instance
        openapi_file_path: Path to the OpenAPI specification file
    """
    
    # Load OpenAPI specification from YAML file
    openapi_path = Path(openapi_file_path)
    if openapi_path.exists():
        with open(openapi_path, 'r', encoding='utf-8') as f:
            openapi_spec = yaml.safe_load(f)
    else:
        # Fallback to generating OpenAPI spec from FastAPI app
        openapi_spec = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
    
    # Custom Swagger UI HTML with enhanced styling
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=f"{app.title} - API Documentation",
            swagger_ui_parameters={
                "deepLinking": True,
                "displayOperationId": True,
                "defaultModelsExpandDepth": 2,
                "defaultModelExpandDepth": 2,
                "defaultModelRendering": "example",
                "displayRequestDuration": True,
                "docExpansion": "list",
                "filter": True,
                "showExtensions": True,
                "showCommonExtensions": True,
                "tryItOutEnabled": True,
                "requestInterceptor": """
                function(request) {
                    // Add authentication header if available
                    const token = localStorage.getItem('access_token');
                    if (token) {
                        request.headers['Authorization'] = 'Bearer ' + token;
                    }
                    return request;
                }
                """,
                "responseInterceptor": """
                function(response) {
                    // Store access token if present in response
                    if (response.body && response.body.access_token) {
                        localStorage.setItem('access_token', response.body.access_token);
                    }
                    return response;
                }
                """
            },
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css"
        )
    
    # Serve OpenAPI JSON
    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi_json():
        return openapi_spec
    
    # Serve OpenAPI YAML
    @app.get("/openapi.yaml", include_in_schema=False)
    async def get_openapi_yaml():
        return yaml.dump(openapi_spec, default_flow_style=False)
    
    # Alternative documentation endpoint
    @app.get("/redoc", include_in_schema=False)
    async def redoc_html():
        from fastapi.openapi.docs import get_redoc_html
        return get_redoc_html(
            openapi_url="/openapi.json",
            title=f"{app.title} - ReDoc Documentation",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"
        )
    
    return app

def create_swagger_config():
    """
    Create a Swagger configuration file for custom settings
    """
    config = {
        "swagger": "2.0",
        "info": {
            "title": "QuantaEnergi ETRM/CTRM API",
            "version": "2.0.0",
            "description": "Comprehensive Energy Trading and Risk Management API"
        },
        "host": "localhost:8000",
        "basePath": "/",
        "schemes": ["http", "https"],
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "securityDefinitions": {
            "BearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        },
        "security": [
            {
                "BearerAuth": []
            }
        ]
    }
    
    with open("swagger_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    return config

if __name__ == "__main__":
    # Create Swagger configuration
    config = create_swagger_config()
    print("Swagger configuration created: swagger_config.json")
    print("To use Swagger UI, import and call setup_swagger_ui(app) in your main.py")
