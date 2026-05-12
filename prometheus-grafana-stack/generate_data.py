import csv
import random
import os
from datetime import datetime, timedelta

PRODUCTS = ["Keyboard", "Monitor", "Mouse", "Headset", "Webcam"]
REGIONS = ["NCR", "Cebu", "Davao", "Iloilo", "Pampanga"]

def generate_sales(num_rows=100):
    os.makedirs("data", exist_ok=True)
    filepath = "data/sales.csv"

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "order_id", "product", "region", "quantity", "price", "timestamp"
        ])
        writer.writeheader()

        for i in range(num_rows):
            writer.writerow({
                "order_id": f"ORD-{i+1:04d}",
                "product": random.choice(PRODUCTS),
                "region": random.choice(REGIONS),
                "quantity": random.randint(1, 20),
                "price": round(random.uniform(500, 5000), 2),
                "timestamp": (datetime.now() - timedelta(minutes=i)).isoformat()
            })

    print(f"✅ Generated {num_rows} rows → {filepath}")

if __name__ == "__main__":
    generate_sales()