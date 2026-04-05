# API Documentation

## Base URL
`http://localhost:5000`

## Endpoints

### Health Check
**GET** `/health`
- Returns: `{"status": "ok"}`
- Status: `200`

### List All Products
**GET** `/products`
- Returns: Array of active products
- Status: `200`
- Example response:
```json
[{"id": 1, "name": "Widget", "category": "Tools", "price": 9.99, "stock": 50, "is_active": true}]
```

### Get Single Product
**GET** `/products/<id>`
- Returns: Single product object
- Status: `200`
- Error: `404` if not found

### Create Product
**POST** `/products`
- Content-Type: `application/json`
- Required fields: `name`, `category`, `price`
- Optional fields: `stock` (defaults to 0)
- Example request:
```json
{"name": "Widget", "category": "Tools", "price": 9.99, "stock": 50}
```
- Status: `201` on success
- Errors: `400` bad input, `409` duplicate name

### Update Product
**PUT** `/products/<id>`
- Content-Type: `application/json`
- All fields optional: `name`, `category`, `price`, `stock`
- Status: `200` on success
- Errors: `404` not found, `400` bad input, `409` duplicate name

### Delete Product
**DELETE** `/products/<id>`
- Soft deletes (sets is_active to false)
- Status: `200` on success
- Error: `404` if not found

## Error Format
All errors return JSON:
```json
{"error": "Description of what went wrong"}
```

## Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad input |
| 404 | Not found |
| 405 | Method not allowed |
| 409 | Conflict (duplicate) |
| 415 | Unsupported media type |
| 500 | Server error |