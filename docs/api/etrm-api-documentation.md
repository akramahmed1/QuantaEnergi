# QuantaEnergi ETRM/CTRM API Documentation

## Overview

This document provides comprehensive API documentation for the QuantaEnergi Energy Trading and Risk Management (ETRM/CTRM) system. The API follows RESTful principles and implements a versioned approach with `/api/v1/` as the current version.

## Base URL

```
Production: https://api.quantaenergi.com/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

All API endpoints require authentication using Bearer tokens:

```http
Authorization: Bearer <your_jwt_token>
```

## Response Format

All API responses follow a consistent format:

```json
{
  "message": "Success message",
  "data": {
    // Response data
  },
  "success": true,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Handling

Error responses follow this format:

```json
{
  "detail": "Error description",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## API Endpoints

### 1. Trading Services

#### Trade Lifecycle Management

##### Create Trade
```http
POST /trades
```

**Request Body:**
```json
{
  "commodity": "crude_oil",
  "quantity": 1000.0,
  "price": 75.50,
  "currency": "USD",
  "counterparty": "GlobalOilCorp",
  "trade_date": "2024-01-15T10:30:00Z",
  "delivery_date": "2024-02-15T10:30:00Z",
  "trade_type": "spot",
  "sharia_compliant": true
}
```

**Response:**
```json
{
  "message": "Trade created successfully",
  "data": {
    "trade_id": "TRD-2024-001",
    "status": "pending_approval",
    "created_at": "2024-01-15T10:30:00Z",
    "workflow_instance_id": "WF-abc123"
  }
}
```

##### Get Trade Details
```http
GET /trades/{trade_id}
```

**Response:**
```json
{
  "message": "Trade details retrieved",
  "data": {
    "trade_id": "TRD-2024-001",
    "commodity": "crude_oil",
    "quantity": 1000.0,
    "price": 75.50,
    "currency": "USD",
    "status": "confirmed",
    "counterparty": "GlobalOilCorp",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

##### Update Trade
```http
PUT /trades/{trade_id}
```

**Request Body:**
```json
{
  "price": 76.00,
  "quantity": 1100.0,
  "notes": "Price adjustment due to market conditions"
}
```

##### Delete Trade
```http
DELETE /trades/{trade_id}
```

#### Sharia Compliance

##### Validate Trade for Sharia Compliance
```http
POST /sharia/validate
```

**Request Body:**
```json
{
  "trade_id": "TRD-2024-001",
  "commodity": "crude_oil",
  "trading_structure": "spot",
  "has_interest": false,
  "asset_backing_ratio": 0.85
}
```

**Response:**
```json
{
  "message": "Sharia validation completed",
  "data": {
    "compliant": true,
    "compliance_score": 95.0,
    "risk_level": "low",
    "recommendations": ["Maintain current compliance practices"]
  }
}
```

##### Calculate Zakat
```http
POST /sharia/zakat
```

**Request Body:**
```json
{
  "asset_value": 1000000.0,
  "currency": "USD",
  "calculation_date": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "message": "Zakat calculation completed",
  "data": {
    "zakat_amount": 25000.0,
    "zakat_rate": 0.025,
    "asset_value": 1000000.0,
    "currency": "USD"
  }
}
```

### 2. Supply Chain Services

#### Supply Chain Management

##### Create Supply Chain
```http
POST /supply-chain
```

**Request Body:**
```json
{
  "commodity": "crude_oil",
  "origin": "Ras Tanura, Saudi Arabia",
  "destination": "Rotterdam, Netherlands",
  "quantity": 100000.0,
  "transport_mode": "pipeline",
  "estimated_cost": 500000.0,
  "estimated_duration_days": 15
}
```

**Response:**
```json
{
  "message": "Supply chain created successfully",
  "data": {
    "supply_chain_id": "SC-2024-001",
    "status": "planned",
    "created_at": "2024-01-15T10:30:00Z",
    "optimization_score": 85.5
  }
}
```

##### Track Supply Chain
```http
GET /supply-chain/{supply_chain_id}/track
```

**Response:**
```json
{
  "message": "Supply chain tracking information",
  "data": {
    "supply_chain_id": "SC-2024-001",
    "current_status": "in_transit",
    "current_location": "Mediterranean Sea",
    "progress_percentage": 65.0,
    "eta": "2024-01-30T15:00:00Z",
    "tracking_history": [
      {
        "timestamp": "2024-01-15T10:30:00Z",
        "status": "departed",
        "location": "Ras Tanura, Saudi Arabia"
      }
    ]
  }
}
```

### 3. Delivery Services

#### Physical Delivery Management

##### Schedule Cargo Delivery
```http
POST /delivery/schedule/cargo
```

**Request Body:**
```json
{
  "commodity": "crude_oil",
  "quantity": 100000.0,
  "origin_port": "Ras Tanura, Saudi Arabia",
  "destination_port": "Rotterdam, Netherlands",
  "loading_date": "2024-01-20T08:00:00Z",
  "eta": "2024-02-10T17:00:00Z",
  "vessel_name": "Super Tanker Alpha",
  "contract_id": "TRD-2024-001"
}
```

**Response:**
```json
{
  "message": "Cargo delivery scheduled successfully",
  "data": {
    "success": true,
    "delivery_id": "CARGO-abc123",
    "delivery_details": {
      "delivery_id": "CARGO-abc123",
      "mode": "cargo_ship",
      "status": "planned",
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

##### Schedule Pipeline Delivery
```http
POST /delivery/schedule/pipeline
```

**Request Body:**
```json
{
  "commodity": "natural_gas",
  "quantity": 500000.0,
  "start_node": "Permian Basin Hub",
  "end_node": "Houston Distribution Center",
  "start_time": "2024-01-25T00:00:00Z",
  "estimated_flow_rate": 10000.0,
  "pipeline_name": "Trans-Texas Pipeline",
  "contract_id": "TRD-2024-002"
}
```

##### Track Delivery
```http
GET /delivery/track/{delivery_id}
```

##### Update Delivery Status
```http
PUT /delivery/status/{delivery_id}
```

**Request Body:**
```json
{
  "status": "in_transit",
  "location": "Mid-Atlantic Ocean",
  "notes": "Vessel encountered minor weather delays",
  "estimated_arrival": "2024-02-12T10:00:00Z"
}
```

##### Get Delivery Analytics
```http
GET /delivery/analytics
```

**Response:**
```json
{
  "message": "Delivery analytics retrieved",
  "data": {
    "analytics": {
      "total_deliveries": 45,
      "status_distribution": {
        "delivered": 40,
        "in_transit": 3,
        "delayed": 2
      },
      "on_time_delivery_rate": 88.9,
      "average_transit_time_hours": 72.5,
      "carbon_footprint_estimates": {
        "total_co2_tons": 1500.0,
        "per_delivery_co2_tons": 3.5
      }
    }
  }
}
```

### 4. Settlement Services

#### Advanced Settlements

##### Create Settlement Batch
```http
POST /settlements/batch
```

**Request Body:**
```json
{
  "trades": [
    {
      "trade_id": "TRD-2024-001",
      "party_a": "QuantaEnergi",
      "party_b": "GlobalOilCorp",
      "amount": 1000000.0,
      "currency": "USD",
      "direction": "buy"
    }
  ],
  "currencies": ["USD", "EUR"],
  "netting_type": "bilateral",
  "created_by": "user_id_123"
}
```

**Response:**
```json
{
  "message": "Settlement batch created successfully",
  "data": {
    "batch_id": "SETTLE_abc123",
    "status": "pending",
    "netting_result": {
      "netting_type": "bilateral",
      "currency_nets": {
        "USD": {
          "total_debits": 1000000.0,
          "total_credits": 0.0,
          "net_amount": -1000000.0
        }
      },
      "party_nets": {
        "QuantaEnergi": {
          "balances": {"USD": -1000000.0},
          "total_exposure": 1000000.0,
          "net_position_usd": -1000000.0
        }
      },
      "netting_efficiency": 85.2
    }
  }
}
```

##### Process Settlement Reconciliation
```http
POST /settlements/reconcile/{batch_id}
```

**Request Body:**
```json
{
  "external_confirmations": [
    {
      "source": "Stripe",
      "transaction_id": "txn_abc123",
      "amount": 1000000.0
    }
  ],
  "total_settled": 1000000.0,
  "settlement_currency": "USD",
  "settlement_method": "wire_transfer",
  "matched_count": 10,
  "unmatched_count": 0
}
```

##### Create Automated Reconciliation Task
```http
POST /settlements/reconcile/automate
```

**Request Body:**
```json
{
  "frequency": "daily",
  "time": "02:00",
  "timezone": "UTC",
  "enabled": true,
  "auto_approve_threshold": 0.01,
  "notification_threshold": 1.0,
  "external_systems": ["stripe", "bank_api"],
  "created_by": "admin_user"
}
```

##### Get Settlement Analytics
```http
GET /settlements/analytics
```

**Query Parameters:**
- `date_from` (optional): Start date for analytics
- `date_to` (optional): End date for analytics

### 5. Reporting Services

#### Report Generation

##### Generate Report
```http
POST /reports/build
```

**Request Body:**
```json
{
  "template_name": "CUSTOM_TRADE_SUMMARY",
  "report_params": {
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "num_entries": 100
  }
}
```

**Response:**
```json
{
  "message": "Report generated successfully",
  "data": {
    "success": true,
    "report_id": "RPT-abc123",
    "status": "generated",
    "preview": [
      {
        "trade_id": "TRADE-abc123",
        "commodity": "Crude Oil",
        "quantity": 1000.0,
        "price": 75.50,
        "trade_date": "2024-01-15T10:30:00Z",
        "counterparty": "GlobalOilCorp",
        "status": "Completed",
        "profit_loss": 25000.0
      }
    ]
  }
}
```

##### Get Report Templates
```http
GET /reports/templates
```

**Response:**
```json
{
  "message": "Report templates retrieved",
  "data": {
    "templates": {
      "FERC_714": {
        "name": "FERC Form 714 - Annual Electric Balancing Authority Report",
        "description": "Standardized report for electric balancing authorities",
        "fields": ["timestamp", "entity_id", "net_generation", "net_interchange", "load", "reserves"],
        "format": "CSV"
      },
      "REMIT_TRANSACTION": {
        "name": "REMIT Transaction Reporting",
        "description": "Report for wholesale energy market transactions under REMIT",
        "fields": ["transaction_id", "contract_id", "commodity", "volume", "price"],
        "format": "XML"
      }
    }
  }
}
```

##### Export Report
```http
POST /reports/{report_id}/export
```

**Request Body:**
```json
{
  "export_format": "PDF"
}
```

**Response:**
```json
{
  "message": "Report exported successfully",
  "data": {
    "success": true,
    "report_id": "RPT-abc123",
    "export_format": "PDF",
    "content_type": "application/pdf",
    "file_content_base64": "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwo...",
    "message": "Mock PDF report generated and base64 encoded"
  }
}
```

### 6. Market Data Services

#### Market Data Normalization

##### Normalize Market Data
```http
POST /market/feed
```

**Request Body:**
```json
{
  "raw_data": {
    "price": 75.50,
    "currency": "USD",
    "timestamp": 1640995200,
    "bid": 75.45,
    "ask": 75.55,
    "volume": 50000
  },
  "data_type": "price",
  "source": "yahoo_finance"
}
```

**Response:**
```json
{
  "message": "Market data normalized successfully",
  "data": {
    "success": true,
    "normalized_data": {
      "symbol": "CL=F",
      "price": 75.50,
      "currency": "USD",
      "timestamp": "2024-01-15T10:30:00Z",
      "source": "yahoo_finance",
      "bid": 75.45,
      "ask": 75.55,
      "volume": 50000,
      "normalized_at": "2024-01-15T10:30:00Z",
      "data_type": "price",
      "normalization_version": "1.0"
    }
  }
}
```

##### Get Market Data
```http
GET /market/data/{symbol}
```

**Query Parameters:**
- `data_type`: Type of data to retrieve (price, volume, volatility, etc.)
- `source` (optional): Source filter

##### Get Market Data Feed
```http
POST /market/feed/batch
```

**Request Body:**
```json
{
  "symbols": ["CL=F", "NG=F", "HO=F"],
  "data_types": ["price", "volume"],
  "sources": ["yahoo_finance", "bloomberg"]
}
```

##### Start Data Feed
```http
POST /market/feed/start
```

**Request Body:**
```json
{
  "symbol": "CL=F",
  "data_type": "price",
  "source": "yahoo_finance",
  "frequency": 60
}
```

##### Stop Data Feed
```http
POST /market/feed/stop/{feed_id}
```

##### Get Active Feeds
```http
GET /market/feeds/active
```

##### Get WebSocket Information
```http
GET /market/websocket/info
```

**Response:**
```json
{
  "message": "WebSocket information retrieved",
  "data": {
    "websocket_url": "ws://localhost:8765",
    "connection_protocol": "JSON",
    "message_types": ["market_data", "connection", "ping", "pong", "subscribe"],
    "subscription_format": {
      "type": "subscribe",
      "symbols": ["CL=F", "NG=F"],
      "data_types": ["price", "volume"]
    }
  }
}
```

### 7. Workflow Services

#### Workflow Management

##### Create Workflow Instance
```http
POST /workflows/approve
```

**Request Body:**
```json
{
  "workflow_template": "trade_approval_workflow",
  "context_data": {
    "trade_id": "TRD-2024-001",
    "amount": 1000000.0,
    "counterparty": "GlobalOilCorp"
  },
  "initiated_by": "user_id_123"
}
```

**Response:**
```json
{
  "message": "Workflow instance created successfully",
  "data": {
    "success": true,
    "workflow_instance": {
      "instance_id": "WF-abc123",
      "template_name": "trade_approval_workflow",
      "status": "in_progress",
      "current_step": "risk_assessment",
      "initiated_by": "user_id_123",
      "initiated_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

##### Approve Workflow Step
```http
POST /workflows/approve/step
```

**Request Body:**
```json
{
  "approval_id": "APR-abc123",
  "approved_by": "user_id_456",
  "approval_notes": "Approved after risk assessment review"
}
```

##### Reject Workflow Step
```http
POST /workflows/reject/step
```

**Request Body:**
```json
{
  "approval_id": "APR-abc123",
  "rejected_by": "user_id_456",
  "rejection_reason": "Insufficient documentation provided"
}
```

##### Get Workflow Instance
```http
GET /workflows/instance/{instance_id}
```

##### Get Pending Approvals
```http
GET /workflows/approvals/pending
```

**Query Parameters:**
- `approver_role` (optional): Filter by approver role

##### Upload Document
```http
POST /workflows/documents/upload
```

**Request Body:**
```json
{
  "workflow_instance_id": "WF-abc123",
  "document_type": "contract",
  "filename": "contract_2024_001.pdf",
  "content_type": "application/pdf",
  "file_size": 1024000,
  "metadata": {
    "contract_type": "futures",
    "expiry_date": "2024-12-31"
  }
}
```

##### Get Workflow Analytics
```http
GET /workflows/analytics
```

##### Get Workflow Templates
```http
GET /workflows/templates
```

##### Get Workflows by Status
```http
GET /workflows/status/{status}
```

##### Get Workflows by User
```http
GET /workflows/user/{user_id}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Standard Users**: 1000 requests per hour
- **Premium Users**: 5000 requests per hour
- **Enterprise Users**: 10000 requests per hour

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## WebSocket API

### Connection

Connect to the WebSocket endpoint:
```javascript
const ws = new WebSocket('ws://localhost:8765');
```

### Message Types

#### Subscribe to Market Data
```json
{
  "type": "subscribe",
  "symbols": ["CL=F", "NG=F"],
  "data_types": ["price", "volume"]
}
```

#### Ping/Pong
```json
{
  "type": "ping"
}
```

#### Market Data Update
```json
{
  "type": "market_data",
  "symbol": "CL=F",
  "data_type": "price",
  "data": {
    "price": 75.50,
    "currency": "USD",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 409 | Conflict - Resource already exists |
| 422 | Unprocessable Entity - Validation error |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Service temporarily unavailable |

## SDKs and Libraries

### JavaScript/TypeScript
```bash
npm install @quantaenergi/api-client
```

### Python
```bash
pip install quantaenergi-api
```

### Java
```xml
<dependency>
  <groupId>com.quantaenergi</groupId>
  <artifactId>api-client</artifactId>
  <version>1.0.0</version>
</dependency>
```

## Support

For API support and questions:
- **Email**: api-support@quantaenergi.com
- **Documentation**: https://docs.quantaenergi.com
- **Status Page**: https://status.quantaenergi.com

## Changelog

### Version 1.0.0 (2024-01-15)
- Initial API release
- Trading services
- Supply chain management
- Delivery services
- Settlement services
- Reporting services
- Market data services
- Workflow management
- WebSocket support
- Comprehensive documentation
