# Ecommerce-platform-with-microservice-architecture

Three independently deployable Flask microservices are included. Their data is kept in memory for this initial implementation.

| Service | Build/run | API |
| --- | --- | --- |
| Product | `docker build -t product-service ./product-service` then `docker run -p 5001:5000 product-service` | `GET /products`, `GET /products/{id}` |
| Cart | `docker build -t cart-service ./cart-service` then `docker run -p 5002:5000 cart-service` | `GET /carts/{cart_id}`, `POST /carts/{cart_id}/items`, `DELETE /carts/{cart_id}/items/{product_id}` |
| Order | `docker build -t order-service ./order-service` then `docker run -p 5003:5000 order-service` | `POST /orders`, `GET /orders`, `GET /orders/{id}` |

Every service also provides `GET /health`. To add an item, send JSON such as `{"product_id":"p-100","quantity":2}`. To create an order, send `{"customer_id":"customer-1","items":[{"product_id":"p-100","quantity":2}]}`.
