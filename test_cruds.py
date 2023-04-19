from bson import ObjectId
from fastapi.testclient import TestClient
from cruds import app, collection

client = TestClient(app)

def test_read_products():
    # Send GET request to API endpoint
    response = client.get("/")
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    response_body = response.json()
    # Get the number of products in the database
    num_products = collection.count_documents({})

    # Check that the number of products in the response is the same as the number of products in the database
    assert len(response_body) == num_products, f"Expected {num_products} products, but got {len(response_body)}"

    # Check that each product in the response has an '_id' field
    for product in response_body:
        assert '_id' in product, "Expected '_id' field in product"



def test_create_product():
    # Create a test product to post
    test_product = {
        "name": "Test Product",
        "description": "A test product",
        "price": 9.99,
        "stock": 5,
        "category": "Test",
    }

    # Post the test product to the API
    response = client.post("/products", json=test_product)

    # Check that the response has a 200 OK status code
    assert response.status_code == 200

    # Check that the response body is the same as the test product, with an added _id field
    response_body = response.json()
    assert response_body["_id"] is not None
    test_product["_id"] = response_body["_id"]
    assert response_body == test_product


def test_delete_product():
    # Create a test product to delete
    test_product = {
        "name": "Test Product",
        "description": "A test product",
        "price": 9.99,
        "stock": 5,
        "category": "Test",
    }
    result = collection.insert_one(test_product)
    product_id = str(result.inserted_id)

    # Delete the test product from the API
    response = client.delete(f"/products/{product_id}")

    # Check that the response has a 200 OK status code
    assert response.status_code == 200

    # Check that the response body has the expected message
    assert response.json() == {"message": "Product deleted successfully"}

    # Check that the product was actually deleted from the database
    assert collection.count_documents({"_id": ObjectId(product_id)}) == 0
