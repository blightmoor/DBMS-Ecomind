import mysql.connector
import random
from datetime import datetime, timedelta

# ---------- DB CONFIG ----------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ukit@2104",
    database="SmartCarbonDB"
)
cursor = db.cursor()

# ---------- PARAMETERS ----------
start_date = datetime(2025, 10, 28)
end_date = datetime(2025, 10, 28)

# Get existing orgs, locations, and categories
cursor.execute("SELECT org_id, location_id, type FROM Locations;")
locations = cursor.fetchall()

cursor.execute("SELECT category_id, name FROM EmissionCategories;")
categories = cursor.fetchall()

# ---------- EMISSION RANGES ----------
def generate_emission(location_type, category_name):
    base = {
        "factory": (200, 800),
        "office": (30, 120),
        "warehouse": (80, 300),
        "plant": (150, 600),
        "lab": (60, 200)
    }

    factor = {
        "Transport": 1.2,
        "Electricity/Energy": 1.5,
        "Industrial Processes": 1.8,
        "Waste Management": 0.9,
        "Raw Materials": 1.4,
        "Packaging & Shipping": 1.3,
        "Office Operations": 0.8
    }

    min_val, max_val = base.get(location_type, (50, 200))
    co2 = random.uniform(min_val, max_val) * factor.get(category_name, 1.0)
    energy = co2 * random.uniform(0.3, 0.6)  # approximate ratio
    return round(co2, 2), round(energy, 2)

# ---------- INSERT DATA ----------
insert_query = """
INSERT INTO DailyEmissions (org_id, location_id, category_id, record_date, co2_emitted, energy_consumed)
VALUES (%s, %s, %s, %s, %s, %s)
"""

current_date = start_date
while current_date <= end_date:
    # Get day of week (0=Monday, 5=Saturday, 6=Sunday)
    day_of_week = current_date.weekday()
    
    for (org_id, location_id, location_type) in locations:
        for (category_id, category_name) in categories:
            co2, energy = generate_emission(location_type, category_name)
            
            # Apply weekend reduction factors
            if day_of_week == 5:  # Saturday
                co2 *= 0.5
                energy *= 0.5
            elif day_of_week == 6:  # Sunday
                co2 *= 0.2  # 1/5th
                energy *= 0.2
            
            co2 = round(co2, 2)
            energy = round(energy, 2)
            
            cursor.execute(insert_query, (org_id, location_id, category_id, current_date.date(), co2, energy))
    current_date += timedelta(days=1)

db.commit()
cursor.close()
db.close()

print("✅ Random emission data inserted successfully!")
