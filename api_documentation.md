# Vendor Management WebApp API Documentation

## Overview

This document provides details on the API endpoints available in the Vendor Management WebApp. The API is built using Django REST Framework and provides CRUD operations for Vendors, Parts, Spends, and Risks, as well as some custom endpoints for analytics.

## Authentication

All API endpoints require authentication. The specific authentication method is not detailed in the provided code, but it's likely to be token-based or session-based authentication.

## API Endpoints

### Vendors

- **Endpoint**: `/api/vendors/`
- **Methods**: GET, POST, PUT, PATCH, DELETE
- **Description**: Manage vendor data
- **Fields**:
  - vendor_name (string)
  - vendor_id (string, unique)
  - payment_terms (string)
  - country (string, optional)
  - average_discount (decimal)
  - contract_type (string, choices: FIXED, TIME, COST)
  - rating (decimal)
  - credit_limit (decimal)
  - contract_year (integer)
  - relationship_type (string, choices: DIRECT, THIRD PARTY)

### Parts

- **Endpoint**: `/api/parts/`
- **Methods**: GET, POST, PUT, PATCH, DELETE
- **Description**: Manage part data
- **Fields**:
  - part_number (string, unique)
  - vendor (foreign key to Vendor)
  - buyer (string)
  - discount (decimal)

### Spends

- **Endpoint**: `/api/spends/`
- **Methods**: GET, POST, PUT, PATCH, DELETE
- **Description**: Manage spend data
- **Fields**:
  - vendor (foreign key to Vendor)
  - year (integer)
  - usd_amount (decimal)
  - relationship_type (string, choices: DIRECT, THIRD PARTY)
  - rank (integer, optional)

### Risks

- **Endpoint**: `/api/risks/`
- **Methods**: GET, POST, PUT, PATCH, DELETE
- **Description**: Manage risk data
- **Fields**:
  - vendor (one-to-one relationship with Vendor)
  - risk_level (string, choices: LOW, MEDIUM, HIGH)
  - total_score (integer)
  - payment_terms_score (integer)
  - spend_score (integer)
  - average_discount_score (integer)
  - contract_score (integer)
  - relationship_type_score (integer)

## Custom Endpoints

### Vendor Performance

- **Endpoint**: `/vendor_performance/`
- **Method**: GET
- **Description**: Retrieve aggregated vendor performance data
- **Response**: JSON array of objects with `avg_rating` and `avg_discount` fields

### Contract Type Distribution

- **Endpoint**: `/contract_type_distribution/`
- **Method**: GET
- **Description**: Retrieve distribution of contract types across vendors
- **Response**: JSON array of objects with `contract_type` and `count` fields

### Risk Distribution

- **Endpoint**: `/risk_distribution/`
- **Method**: GET
- **Description**: Retrieve distribution of risk levels across vendors
- **Response**: JSON array of objects with `risk_level` and `count` fields

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests. Common status codes include:

- 200 OK: Successful request
- 201 Created: Successful creation of a new resource
- 400 Bad Request: Invalid input
- 401 Unauthorized: Authentication failed
- 403 Forbidden: User doesn't have permission to perform the requested action
- 404 Not Found: Requested resource not found
- 500 Internal Server Error: Server-side error

Detailed error messages are likely to be included in the response body for client-side errors (4xx status codes).

## Pagination

The API likely uses pagination for list endpoints, but the specific pagination details are not provided in the code. Typically, Django REST Framework uses limit/offset pagination by default.

## Filtering and Sorting

The API may support filtering and sorting for list endpoints, particularly for the Vendor list. Common query parameters might include:

- `search`: For text-based searching across vendor name and ID
- `relationship_type`: Filter vendors by relationship type
- `risk_level`: Filter vendors by risk level
- `sort_by`: Field to sort results by
- `sort_order`: Ascending or descending order

Please refer to the specific endpoint implementations for more details on supported query parameters.

---

Note: This documentation is based on the provided code and may not be exhaustive. Always refer to the latest codebase and server configurations for the most up-to-date and accurate information.