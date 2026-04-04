from locust import HttpUser, task, between


class ProductUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def list_products(self):
        self.client.get("/products")

    @task(2)
    def get_health(self):
        self.client.get("/health")

    @task(1)
    def create_product(self):
        import random
        self.client.post("/products", json={
            "name": f"Product-{random.randint(1, 999999)}",
            "category": "Test",
            "price": round(random.uniform(1, 100), 2),
            "stock": random.randint(1, 500)
        })