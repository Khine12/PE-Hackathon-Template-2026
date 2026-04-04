# Failure Modes Documentation

## Error Handling

All errors return clean JSON responses, never raw stack traces.

| Scenario | Status Code | Response |
|---|---|---|
| Resource not found | 404 | `{"error": "Product not found"}` |
| Missing required fields | 400 | `{"error": "Missing required fields: name, category"}` |
| Invalid data type | 400 | `{"error": "Price must be a number"}` |
| Negative values | 400 | `{"error": "Price must be non-negative"}` |
| Duplicate name | 409 | `{"error": "A product with that name already exists"}` |
| Non-JSON request body | 415 | Unsupported Media Type |
| Empty string input | 400 | `{"error": "Name must be a non-empty string"}` |
| Deleted resource access | 404 | `{"error": "Product not found"}` |

## Failure Scenarios

### 1. Application Crash
- **What happens:** Docker restart policy (`restart: always`) automatically restarts the container
- **Recovery time:** ~2-5 seconds
- **Data impact:** None — PostgreSQL runs in a separate container

### 2. Database Connection Lost
- **What happens:** Peewee's `teardown_appcontext` closes connections on every request, and `before_request` opens new ones with `reuse_if_open=True`
- **Recovery:** Automatic on next request when DB is back

### 3. Bad Input Data
- **What happens:** All inputs are validated before database operations
- **Recovery:** Clean JSON error returned, no crash, no bad data stored

### 4. Duplicate Data
- **What happens:** Unique constraint on product name catches duplicates
- **Recovery:** Returns 409 Conflict with descriptive error message

### 5. Deleted Resource Access
- **What happens:** Soft delete (is_active=False) means data is preserved
- **Recovery:** GET returns 404, data can be restored if needed