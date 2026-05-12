import sqlite3
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_PATH = "data/sales.db"
PORT = 8000

def get_metrics():
    if not os.path.exists(DB_PATH):
        return {"total_orders": 0, "total_revenue": 0, "total_quantity": 0}

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM sales")
    total_orders = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(total), 0) FROM sales")
    total_revenue = round(cur.fetchone()[0], 2)

    cur.execute("SELECT COALESCE(SUM(quantity), 0) FROM sales")
    total_quantity = cur.fetchone()[0]

    cur.execute("""
        SELECT product, COUNT(*) as cnt
        FROM sales GROUP BY product
        ORDER BY cnt DESC LIMIT 1
    """)
    top = cur.fetchone()
    top_product = top[0] if top else "none"
    top_count = top[1] if top else 0

    conn.close()
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_quantity": total_quantity,
        "top_product": top_product,
        "top_product_count": top_count,
    }

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            m = get_metrics()
            output = f"""# HELP dataops_total_orders Total number of orders processed
# TYPE dataops_total_orders gauge
dataops_total_orders {m['total_orders']}

# HELP dataops_total_revenue Total revenue in PHP
# TYPE dataops_total_revenue gauge
dataops_total_revenue {m['total_revenue']}

# HELP dataops_total_quantity Total units sold
# TYPE dataops_total_quantity gauge
dataops_total_quantity {m['total_quantity']}

# HELP dataops_top_product_count Order count of top product
# TYPE dataops_top_product_count gauge
dataops_top_product_count {m['top_product_count']}
"""
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(output.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress access logs

if __name__ == "__main__":
    print(f"✅ Metrics exporter running at http://localhost:{PORT}/metrics")
    print("   Press Ctrl+C to stop")
    HTTPServer(("0.0.0.0", PORT), MetricsHandler).serve_forever()