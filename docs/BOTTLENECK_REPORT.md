# Bottleneck Report

## Initial Bottleneck

During load testing with 500 concurrent users, Flask's built-in development server
hit a 41% error rate. The dev server is single-threaded, meaning it can only process
one request at a time. Under heavy load, requests queued up, timed out, and returned
500 errors.

## What We Changed

**1. Switched to Gunicorn (Production WSGI Server)**
Replaced Flask's dev server with Gunicorn running 4 worker processes per container.
With 2 app containers, this gives us 8 parallel workers handling requests simultaneously.

**2. Added Redis Caching**
GET /products was hitting PostgreSQL on every request. We added Redis as an in-memory
cache with a 30-second TTL. Repeated reads now serve from Redis instead of querying
the database, reducing DB load significantly.

**3. Nginx Load Balancer**
Nginx distributes incoming traffic evenly across both app containers, preventing any
single container from becoming overwhelmed.

## Results

| Metric         | Before (Flask Dev Server) | After (Gunicorn + Redis + Nginx) |
|----------------|--------------------------|----------------------------------|
| Error Rate     | 41.78%                   | 0.00%                            |
| Avg Response   | 4,528 ms                 | 3,047 ms                         |
| Throughput     | 57.51 req/s              | 76.72 req/s                      |
| Max Response   | 11,009 ms                | 6,958 ms                         |

## Conclusion

The primary bottleneck was Flask's single-threaded dev server. Gunicorn eliminated
the errors entirely. Redis caching and Nginx load balancing further improved response
times and throughput. The system now handles 500 concurrent users with zero failures.