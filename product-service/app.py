from flask import Flask, jsonify

app = Flask(__name__)

PRODUCTS = [
    {"id": "p-100", "name": "Wireless Mouse", "price": 24.99, "currency": "USD", "in_stock": True},
    {"id": "p-101", "name": "Mechanical Keyboard", "price": 79.99, "currency": "USD", "in_stock": True},
    {"id": "p-102", "name": "USB-C Hub", "price": 39.99, "currency": "USD", "in_stock": False},
]


@app.get("/health")
def health():
    return {"status": "ok", "service": "product-service"}


@app.get("/products")
def list_products():
    return jsonify({"products": PRODUCTS})


@app.get("/products/<product_id>")
def get_product(product_id):
    product = next((item for item in PRODUCTS if item["id"] == product_id), None)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
