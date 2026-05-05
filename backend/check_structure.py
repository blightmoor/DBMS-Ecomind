import mysql.connector

CONFIG = dict(host='localhost', user='root', password='Ukit@2104', database='SmartCarbonDB')

def describe_table(cursor, name):
    print(f"\n=== {name} ===")
    cursor.execute(f"DESCRIBE {name}")
    for row in cursor.fetchall():
        print(row)

def count_rows(cursor, name):
    cursor.execute(f"SELECT COUNT(*) FROM {name}")
    cnt = cursor.fetchone()[0]
    print(f"Rows in {name}: {cnt}")

if __name__ == "__main__":
    db = mysql.connector.connect(**CONFIG)
    cur = db.cursor()

    # List tables
    print("Existing tables:")
    cur.execute("SHOW TABLES")
    for (t,) in cur.fetchall():
        print("-", t)

    # Describe core tables
    for t in [
        'Organizations', 'Users', 'Locations', 'EmissionCategories', 'DailyEmissions'
    ]:
        describe_table(cur, t)
        count_rows(cur, t)

    # Sample a few records to validate joins
    print("\nSample EmissionCategories:")
    cur.execute("SELECT category_id, name FROM EmissionCategories LIMIT 5")
    for r in cur.fetchall():
        print(r)

    print("\nSample Locations:")
    cur.execute("SELECT location_id, org_id, name, type FROM Locations LIMIT 5")
    for r in cur.fetchall():
        print(r)

    print("\nSample DailyEmissions:")
    cur.execute("SELECT emission_id, org_id, location_id, category_id, record_date, co2_emitted FROM DailyEmissions ORDER BY record_date DESC LIMIT 5")
    for r in cur.fetchall():
        print(r)

    cur.close(); db.close()
