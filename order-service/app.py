from uuid import uuid4

from flask import Flask, jsonify, request

app = Flask(__name__)
ORDERS = {}


@app.get("/health")
def health():
    return {"status": "ok", "service": "order-service"}


@app.post("/orders")
def create_order():
    data = request.get_json(silent=True) or {}
    customer_id = data.get("customer_id")
    items = data.get("items")
    if not isinstance(customer_id, str) or not customer_id or not isinstance(items, list) or not items:
        return jsonify({"error": "customer_id and a non-empty items list are required"}), 400

    if any(not isinstance(item, dict) or not item.get("product_id") or not isinstance(item.get("quantity"), int) or item["quantity"] < 1 for item in items):
        return jsonify({"error": "Each item requires product_id and a positive integer quantity"}), 400

    order = {
        "id": str(uuid4()),
        "customer_id": customer_id,
        "items": items,
        "status": "created",
    }
    ORDERS[order["id"]] = order
    return jsonify(order), 201


@app.get("/orders")
def list_orders():
    return jsonify({"orders": list(ORDERS.values())})


@app.get("/orders/<order_id>")
def get_order(order_id):
    order = ORDERS.get(order_id)
    if order is None:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
