from flask import Flask, jsonify, request

app = Flask(__name__)
CARTS = {}


@app.get("/health")
def health():
    return {"status": "ok", "service": "cart-service"}


@app.get("/carts/<cart_id>")
def get_cart(cart_id):
    return jsonify({"id": cart_id, "items": CARTS.get(cart_id, [])})


@app.post("/carts/<cart_id>/items")
def add_item(cart_id):
    data = request.get_json(silent=True) or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    if not isinstance(product_id, str) or not product_id or not isinstance(quantity, int) or quantity < 1:
        return jsonify({"error": "product_id and a positive integer quantity are required"}), 400

    items = CARTS.setdefault(cart_id, [])
    item = next((entry for entry in items if entry["product_id"] == product_id), None)
    if item:
        item["quantity"] += quantity
    else:
        items.append({"product_id": product_id, "quantity": quantity})
    return jsonify({"id": cart_id, "items": items}), 201


@app.delete("/carts/<cart_id>/items/<product_id>")
def remove_item(cart_id, product_id):
    items = CARTS.get(cart_id, [])
    remaining_items = [item for item in items if item["product_id"] != product_id]
    if len(remaining_items) == len(items):
        return jsonify({"error": "Item not found in cart"}), 404
    CARTS[cart_id] = remaining_items
    return jsonify({"id": cart_id, "items": remaining_items})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
