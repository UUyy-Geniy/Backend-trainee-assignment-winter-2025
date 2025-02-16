from locust import HttpUser, task, between
import random

class ShopUser(HttpUser):
    wait_time = between(0.5, 2)
    
    @task(3)
    def view_info(self):
        self.client.get("/api/v1/info", headers=self.headers)
    
    @task(2)
    def buy_item(self):
        items = ["t-shirt", "cup", "book", "pen"]
        self.client.get(
            f"/api/v1/buy/{random.choice(items)}",
            headers=self.headers
        )
    
    @task(1)
    def send_coins(self):
        self.client.post(
            "/api/v1/sendCoin",
            json={"toUser": f"user{random.randint(1,100)}", "amount": 10},
            headers=self.headers
        )
    
    def on_start(self):
        # Аутентификация перед началом
        user_id = random.randint(1, 10000)
        auth = self.client.post("/api/v1/auth", json={
            "username": f"user{user_id}",
            "password": "pass"
        }).json()
        self.headers = {"Authorization": f"Bearer {auth['token']}"}