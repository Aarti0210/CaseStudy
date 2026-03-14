"""
Swagger/OpenAPI documentation for Judicial Supreme Backend API.
"""

from flask import Blueprint, jsonify, render_template_string
from flask_jwt_extended import jwt_required
from app.middleware.rbac import role_required

docs_bp = Blueprint("docs", __name__)

# Swagger UI HTML template
SWAGGER_UI_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Judicial Supreme Backend API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
        .swagger-ui .topbar { display: none; }
        .swagger-ui .info { margin: 50px 0; }
        .swagger-ui .scheme-container { margin: 50px 0; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: '/api/v1/docs/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                validatorUrl: null
            });
        };
    </script>
</body>
</html>
"""

@docs_bp.route("/", methods=["GET"])
def swagger_ui():
    """Serve Swagger UI documentation."""
    return render_template_string(SWAGGER_UI_TEMPLATE)

@docs_bp.route("/openapi.json", methods=["GET"])
def openapi_spec():
    """Serve OpenAPI specification."""
    return jsonify({
        "openapi": "3.0.3",
        "info": {
            "title": "Judicial Supreme Backend API",
            "description": "Backend API for Judicial Supreme case management system",
            "version": "1.0.0",
            "contact": {
                "name": "API Support",
                "email": "support@judicial-supreme.com"
            }
        },
        "servers": [
            {
                "url": "/api/v1",
                "description": "Production server"
            }
        ],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            },
            "schemas": {
                "SuccessResponse": {
                    "type": "object",
                    "properties": {
                        "success": {
                            "type": "boolean",
                            "example": True
                        },
                        "data": {
                            "type": "object"
                        },
                        "message": {
                            "type": "string",
                            "example": "Operation completed successfully"
                        }
                    }
                },
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "success": {
                            "type": "boolean",
                            "example": False
                        },
                        "message": {
                            "type": "string",
                            "example": "Error occurred"
                        },
                        "error": {
                            "type": "string",
                            "example": "ValidationError"
                        }
                    }
                },
                "Pagination": {
                    "type": "object",
                    "properties": {
                        "total": {
                            "type": "integer",
                            "example": 100
                        },
                        "limit": {
                            "type": "integer",
                            "example": 20
                        },
                        "offset": {
                            "type": "integer",
                            "example": 0
                        },
                        "has_next": {
                            "type": "boolean",
                            "example": True
                        },
                        "has_prev": {
                            "type": "boolean",
                            "example": False
                        }
                    }
                },
                "Case": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "example": 1
                        },
                        "title": {
                            "type": "string",
                            "example": "Contract Dispute Case"
                        },
                        "description": {
                            "type": "string",
                            "example": "Breach of contract case"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["Pending", "Active", "Closed", "On Hold"],
                            "example": "Active"
                        },
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2026-03-14T12:00:00Z"
                        },
                        "created_by": {
                            "type": "integer",
                            "example": 1
                        },
                        "assigned_judge_id": {
                            "type": "integer",
                            "example": 2
                        }
                    }
                },
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "example": 1
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "example": "user@example.com"
                        },
                        "role": {
                            "type": "string",
                            "enum": ["admin", "judge", "lawyer", "citizen"],
                            "example": "lawyer"
                        }
                    }
                }
            }
        },
        "security": [
            {
                "bearerAuth": []
            }
        ],
        "paths": {
            "/auth/login": {
                "post": {
                    "tags": ["Authentication"],
                    "summary": "User login",
                    "description": "Authenticate user and return JWT tokens",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["email", "password"],
                                    "properties": {
                                        "email": {
                                            "type": "string",
                                            "format": "email"
                                        },
                                        "password": {
                                            "type": "string",
                                            "minLength": 6
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Login successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "allOf": [
                                            {"$ref": "#/components/schemas/SuccessResponse"},
                                            {
                                                "type": "object",
                                                "properties": {
                                                    "data": {
                                                        "type": "object",
                                                        "properties": {
                                                            "access_token": {"type": "string"},
                                                            "refresh_token": {"type": "string"},
                                                            "user": {"$ref": "#/components/schemas/User"}
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        },
                        "401": {
                            "$ref": "#/components/responses/Unauthorized"
                        }
                    }
                }
            },
            "/case": {
                "get": {
                    "tags": ["Cases"],
                    "summary": "Get all cases",
                    "description": "Retrieve paginated list of cases",
                    "security": [{"bearerAuth": []}],
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Number of items per page",
                            "schema": {
                                "type": "integer",
                                "default": 20,
                                "maximum": 100
                            }
                        },
                        {
                            "name": "offset",
                            "in": "query",
                            "description": "Number of items to skip",
                            "schema": {
                                "type": "integer",
                                "default": 0,
                                "minimum": 0
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Cases retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "allOf": [
                                            {"$ref": "#/components/schemas/SuccessResponse"},
                                            {
                                                "type": "object",
                                                "properties": {
                                                    "data": {
                                                        "type": "object",
                                                        "properties": {
                                                            "items": {
                                                                "type": "array",
                                                                "items": {"$ref": "#/components/schemas/Case"}
                                                            },
                                                            "pagination": {"$ref": "#/components/schemas/Pagination"}
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "tags": ["Cases"],
                    "summary": "Create new case",
                    "description": "Create a new case",
                    "security": [{"bearerAuth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["title"],
                                    "properties": {
                                        "title": {
                                            "type": "string",
                                            "maxLength": 200
                                        },
                                        "description": {
                                            "type": "string"
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Case created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "allOf": [
                                            {"$ref": "#/components/schemas/SuccessResponse"},
                                            {
                                                "type": "object",
                                                "properties": {
                                                    "data": {
                                                        "type": "object",
                                                        "properties": {
                                                            "case": {"$ref": "#/components/schemas/Case"}
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/health": {
                "get": {
                    "tags": ["Health"],
                    "summary": "Health check",
                    "description": "Check API and database health status",
                    "responses": {
                        "200": {
                            "description": "Service healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {
                                                "type": "string",
                                                "example": "ok"
                                            },
                                            "service": {
                                                "type": "string",
                                                "example": "judicial-backend"
                                            },
                                            "timestamp": {
                                                "type": "string",
                                                "format": "date-time"
                                            },
                                            "checks": {
                                                "type": "object",
                                                "properties": {
                                                    "db": {
                                                        "type": "boolean"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "503": {
                            "description": "Service unhealthy"
                        }
                    }
                }
            }
        },
        "tags": [
            {
                "name": "Authentication",
                "description": "User authentication and authorization"
            },
            {
                "name": "Cases",
                "description": "Case management operations"
            },
            {
                "name": "Documents",
                "description": "Document management and file uploads"
            },
            {
                "name": "Hearings",
                "description": "Hearing scheduling and management"
            },
            {
                "name": "Notifications",
                "description": "User notifications"
            },
            {
                "name": "Payments",
                "description": "Payment processing"
            },
            {
                "name": "AI Services",
                "description": "AI-powered legal services"
            },
            {
                "name": "Audit",
                "description": "Audit logs and system monitoring"
            },
            {
                "name": "Health",
                "description": "Health checks and monitoring"
            }
        ]
    })
