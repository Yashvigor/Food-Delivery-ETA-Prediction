import os
import sqlite3
import datetime
import random
from typing import Dict, Any, List, Union

# Try to import PostgreSQL dependencies
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "logistics.db"))

def get_connection():
    """
    Establishes a connection to PostgreSQL if environment variables are set,
    otherwise falls back to SQLite.
    """
    # Check if PostgreSQL environment variables are set
    pg_host = os.environ.get("DB_HOST")
    pg_name = os.environ.get("DB_NAME")
    pg_user = os.environ.get("DB_USER")
    pg_pwd = os.environ.get("DB_PASSWORD")
    pg_port = os.environ.get("DB_PORT", "5432")

    if HAS_POSTGRES and pg_host and pg_name and pg_user and pg_pwd:
        try:
            conn = psycopg2.connect(
                host=pg_host,
                database=pg_name,
                user=pg_user,
                password=pg_pwd,
                port=pg_port
            )
            return conn, "postgresql"
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}. Falling back to SQLite.")
            
    # SQLite fallback
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    # Enable dict factory for SQLite to mimic PostgreSQL RealDictCursor
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"

def execute_query(query: str, params: tuple = ()) -> None:
    """Executes a non-returning query (INSERT/UPDATE/CREATE)."""
    conn, db_type = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_select(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Executes a select query and returns list of dictionaries."""
    conn, db_type = get_connection()
    try:
        if db_type == "postgresql":
            cur = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cur = conn.cursor()
            
        cur.execute(query, params)
        rows = cur.fetchall()
        
        # Format rows as standard dictionary lists
        if db_type == "postgresql":
            return [dict(row) for row in rows]
        else:
            return [dict(row) for row in rows]
    except Exception as e:
        raise e
    finally:
        conn.close()

def init_db():
    """
    Initializes PostgreSQL / SQLite tables and seeds Couriers and Restaurants.
    """
    conn, db_type = get_connection()
    cur = conn.cursor()
    
    print(f"Initializing database using: {db_type.upper()}")
    
    if db_type == "postgresql":
        # Create PostgreSQL tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Couriers (
                courier_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                experience INT NOT NULL,
                vehicle_type VARCHAR(50) NOT NULL,
                rating FLOAT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Restaurants (
                restaurant_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                rating FLOAT NOT NULL,
                location VARCHAR(200) NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Orders (
                order_id VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(50) NOT NULL,
                restaurant_id VARCHAR(50) REFERENCES Restaurants(restaurant_id),
                courier_id VARCHAR(50) REFERENCES Couriers(courier_id),
                distance_km FLOAT NOT NULL,
                order_time TIMESTAMP NOT NULL,
                delivery_time TIMESTAMP,
                predicted_eta FLOAT,
                actual_eta FLOAT,
                status VARCHAR(50) NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Predictions (
                prediction_id SERIAL PRIMARY KEY,
                order_id VARCHAR(50) NOT NULL,
                predicted_time FLOAT NOT NULL,
                confidence_score FLOAT NOT NULL,
                prediction_timestamp TIMESTAMP NOT NULL
            );
        """)
    else:
        # Create SQLite tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Couriers (
                courier_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                experience INTEGER NOT NULL,
                vehicle_type TEXT NOT NULL,
                rating REAL NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Restaurants (
                restaurant_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                rating REAL NOT NULL,
                location TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                restaurant_id TEXT REFERENCES Restaurants(restaurant_id),
                courier_id TEXT REFERENCES Couriers(courier_id),
                distance_km REAL NOT NULL,
                order_time TIMESTAMP NOT NULL,
                delivery_time TIMESTAMP,
                predicted_eta REAL,
                actual_eta REAL,
                status TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Predictions (
                prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                predicted_time REAL NOT NULL,
                confidence_score REAL NOT NULL,
                prediction_timestamp TIMESTAMP NOT NULL
            );
        """)
        
    conn.commit()
    
    # Check if table has data. If not, seed reference data.
    cur.execute("SELECT COUNT(*) FROM Couriers")
    couriers_count = cur.fetchone()[0]
    
    if couriers_count == 0:
        print("Seeding database with default Couriers and Restaurants...")
        
        # Seed Couriers
        couriers_data = [
            ("C0001", "Alex Mercer", 8, "Bike", 4.8),
            ("C0002", "Elena Vance", 12, "Bike", 4.9),
            ("C0003", "James Holden", 3, "Scooter", 4.2),
            ("C0004", "Naomi Nagata", 10, "Scooter", 4.7),
            ("C0005", "Amos Burton", 15, "Bike", 4.6),
            ("C0006", "Chrisjen A.", 1, "Cycle", 3.8),
            ("C0007", "Bobbie Draper", 6, "Bike", 4.5),
            ("C0008", "Clarissa Mao", 2, "Cycle", 4.0),
            ("C0009", "Joseph Miller", 4, "Scooter", 4.1),
            ("C0010", "Camina Drummer", 7, "Scooter", 4.4)
        ]
        
        for c in couriers_data:
            cur.execute(
                "INSERT INTO Couriers (courier_id, name, experience, vehicle_type, rating) VALUES (?, ?, ?, ?, ?)" if db_type == "sqlite" 
                else "INSERT INTO Couriers (courier_id, name, experience, vehicle_type, rating) VALUES (%s, %s, %s, %s, %s)",
                c
            )
            
        # Seed Restaurants
        restaurants_data = [
            ("R0001", "The Burger Capital", 4.6, "45.7725,-122.6801"),
            ("R0002", "Pizzeria Napoli", 4.8, "45.7892,-122.6912"),
            ("R0003", "Wok & Roll Asian", 4.3, "45.7610,-122.6710"),
            ("R0004", "Green Garden Salads", 4.5, "45.7680,-122.6840"),
            ("R0005", "Royal Indian Spices", 4.7, "45.7801,-122.6620")
        ]
        
        for r in restaurants_data:
            cur.execute(
                "INSERT INTO Restaurants (restaurant_id, name, rating, location) VALUES (?, ?, ?, ?)" if db_type == "sqlite"
                else "INSERT INTO Restaurants (restaurant_id, name, rating, location) VALUES (%s, %s, %s, %s)",
                r
            )
            
        # Seed some active simulated orders for the live admin dashboard
        seed_orders(cur, db_type)
            
    conn.commit()
    conn.close()
    print("Database initialization complete.")

def seed_orders(cur, db_type):
    """Seeds some dummy orders with history to populate standard admin analytics."""
    now = datetime.datetime.now()
    
    # 50 historical delivered orders
    for idx in range(1, 51):
        order_id = f"SEED{idx:03d}"
        cust_id = f"CUST{random.randint(100, 999)}"
        rest_id = f"R{random.randint(1, 5):04d}"
        cour_id = f"C{random.randint(1, 10):04d}"
        dist = round(random.uniform(1.2, 12.5), 2)
        
        # Order time distributed over the last 5 days
        days_ago = random.randint(0, 5)
        hours_ago = random.randint(1, 12)
        order_time = now - datetime.timedelta(days=days_ago, hours=hours_ago)
        
        actual_eta = round(random.uniform(18.0, 55.0), 1)
        pred_eta = round(actual_eta + random.uniform(-4.0, 4.0), 1)
        delivery_time = order_time + datetime.timedelta(minutes=actual_eta)
        status = "Delivered"
        
        q_order = (
            "INSERT INTO Orders (order_id, customer_id, restaurant_id, courier_id, distance_km, order_time, delivery_time, predicted_eta, actual_eta, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" if db_type == "sqlite"
            else "INSERT INTO Orders (order_id, customer_id, restaurant_id, courier_id, distance_km, order_time, delivery_time, predicted_eta, actual_eta, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        cur.execute(q_order, (order_id, cust_id, rest_id, cour_id, dist, order_time, delivery_time, pred_eta, actual_eta, status))
        
        q_pred = (
            "INSERT INTO Predictions (order_id, predicted_time, confidence_score, prediction_timestamp) VALUES (?, ?, ?, ?)" if db_type == "sqlite"
            else "INSERT INTO Predictions (order_id, predicted_time, confidence_score, prediction_timestamp) VALUES (%s, %s, %s, %s)"
        )
        cur.execute(q_pred, (order_id, pred_eta, round(random.uniform(85, 98), 1), order_time))

    # 5 currently active orders
    active_statuses = ["Pending", "Preparing", "In Transit"]
    for idx in range(51, 56):
        order_id = f"SEED{idx:03d}"
        cust_id = f"CUST{random.randint(100, 999)}"
        rest_id = f"R{random.randint(1, 5):04d}"
        cour_id = f"C{random.randint(1, 10):04d}"
        dist = round(random.uniform(1.2, 8.5), 2)
        
        # Ordered recently
        mins_ago = random.randint(5, 30)
        order_time = now - datetime.timedelta(minutes=mins_ago)
        
        pred_eta = round(random.uniform(22.0, 48.0), 1)
        status = random.choice(active_statuses)
        
        q_order = (
            "INSERT INTO Orders (order_id, customer_id, restaurant_id, courier_id, distance_km, order_time, delivery_time, predicted_eta, actual_eta, status) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, NULL, ?)" if db_type == "sqlite"
            else "INSERT INTO Orders (order_id, customer_id, restaurant_id, courier_id, distance_km, order_time, delivery_time, predicted_eta, actual_eta, status) VALUES (%s, %s, %s, %s, %s, %s, NULL, %s, NULL, %s)"
        )
        cur.execute(q_order, (order_id, cust_id, rest_id, cour_id, dist, order_time, pred_eta, status))
        
        q_pred = (
            "INSERT INTO Predictions (order_id, predicted_time, confidence_score, prediction_timestamp) VALUES (?, ?, ?, ?)" if db_type == "sqlite"
            else "INSERT INTO Predictions (order_id, predicted_time, confidence_score, prediction_timestamp) VALUES (%s, %s, %s, %s)"
        )
        cur.execute(q_pred, (order_id, pred_eta, round(random.uniform(80, 95), 1), order_time))

if __name__ == "__main__":
    init_db()
