import pytest
from app import create_app
from app.database import db
from app.models.product import Product


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True

    with app.app_context():
        db.create_tables([Product])
        yield app
        Product.delete().execute()


@pytest.fixture
def client(app):
    return app.test_client()


# ============ HEALTH CHECK ============

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


# ============ CREATE PRODUCT ============

def test_create_product(client):
    res = client.post("/products", json={
        "name": "Widget",
        "category": "Tools",
        "price": 9.99,
        "stock": 50
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data["name"] == "Widget"
    assert data["category"] == "Tools"
    assert float(data["price"]) == 9.99
    assert data["stock"] == 50


def test_create_product_missing_fields(client):
    res = client.post("/products", json={"name": "Widget"})
    assert res.status_code == 400
    assert "Missing required fields" in res.get_json()["error"]


def test_create_product_empty_name(client):
    res = client.post("/products", json={
        "name": "",
        "category": "Tools",
        "price": 9.99
    })
    assert res.status_code == 400


def test_create_product_negative_price(client):
    res = client.post("/products", json={
        "name": "Widget",
        "category": "Tools",
        "price": -5
    })
    assert res.status_code == 400


def test_create_product_invalid_price(client):
    res = client.post("/products", json={
        "name": "Widget",
        "category": "Tools",
        "price": "abc"
    })
    assert res.status_code == 400


def test_create_product_duplicate_name(client):
    client.post("/products", json={
        "name": "Widget",
        "category": "Tools",
        "price": 9.99
    })
    res = client.post("/products", json={
        "name": "Widget",
        "category": "Other",
        "price": 5.00
    })
    assert res.status_code == 409


def test_create_product_no_json(client):
    res = client.post("/products", data="not json", content_type="text/plain")
    assert res.status_code in (400, 415)


def test_create_product_negative_stock(client):
    res = client.post("/products", json={
        "name": "Widget",
        "category": "Tools",
        "price": 9.99,
        "stock": -10
    })
    assert res.status_code == 400


# ============ GET PRODUCTS ============

def test_list_products_empty(client):
    res = client.get("/products")
    assert res.status_code == 200
    assert res.get_json() == []


def test_list_products(client):
    client.post("/products", json={
        "name": "Widget",
        "category": "Tools",
        "price": 9.99,
        "stock": 50
    })
    res = client.get("/products")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Widget"


def test_get_product(client):
    create_res = client.post("/products", json={
        "name": "Widget",
        "category": "Tools",
        "price": 9.99,
        "stock": 50
    })
    product_id = create_res.get_json()["id"]
    res = client.get(f"/products/{product_id}")
    assert res.status_code == 200
    assert res.get_json()["name"] == "Widget"


def test_get_product_not_found(client):
    res = client.get("/products/9999")
    assert res.status_code == 404


# ============ UPDATE PRODUCT ============

def test_update_product(client):
    create_res = client.post("/products", json={
        "name": "Widget",
        "category": "Tools",
        "price": 9.99,
        "stock": 50
    })
    product_id = create_res.get_json()["id"]
    res = client.put(f"/products/{product_id}", json={
        "name": "Super Widget",
        "price": 19.99
    })
    assert res.status_code == 200
    assert res.get_json()["name"] == "Super Widget"
    assert float(res.get_json()["price"]) == 19.99


def test_update_product_not_found(client):
    res = client.put("/products/9999", json={"name": "Ghost"})
    assert res.status_code == 404


def test_update_product_invalid_price(client):
    create_res = client.post("/products", json={
        "name": "Widget",
        "category": "Tools",
        "price": 9.99
    })
    product_id = create_res.get_json()["id"]
    res = client.put(f"/products/{product_id}", json={"price": "free"})
    assert res.status_code == 400


# ============ DELETE PRODUCT ============

def test_delete_product(client):
    create_res = client.post("/products", json={
        "name": "Widget",
        "category": "Tools",
        "price": 9.99,
        "stock": 50
    })
    product_id = create_res.get_json()["id"]
    res = client.delete(f"/products/{product_id}")
    assert res.status_code == 200

    # Should not appear in list anymore
    list_res = client.get("/products")
    assert len(list_res.get_json()) == 0


def test_delete_product_not_found(client):
    res = client.delete("/products/9999")
    assert res.status_code == 404


def test_deleted_product_not_accessible(client):
    create_res = client.post("/products", json={
        "name": "Widget",
        "category": "Tools",
        "price": 9.99
    })
    product_id = create_res.get_json()["id"]
    client.delete(f"/products/{product_id}")
    res = client.get(f"/products/{product_id}")
    assert res.status_code == 404