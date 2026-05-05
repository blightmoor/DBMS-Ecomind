import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def seed_organizations():
    """
    Seed the Organizations table with sample data
    """
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        
        cursor = connection.cursor()
        
        # Sample organizations
        organizations = [
            ("GreenTech Solutions", "Technology", "Achieve carbon neutrality by 2030 through renewable energy adoption and sustainable practices", "2024-01-15"),
            ("EcoManufacturing Corp", "Manufacturing", "Reduce emissions by 50% and implement circular economy principles", "2024-02-20"),
            ("Sustainable Retail Inc", "Retail", "Zero waste operations and 100% sustainable supply chain by 2028", "2024-03-10"),
            ("CleanEnergy Power", "Energy", "Transition to 100% renewable energy generation and storage", "2024-01-05"),
            ("Green Logistics Ltd", "Transportation", "Electric fleet conversion and carbon-neutral deliveries", "2024-04-12"),
            ("EcoFood Services", "Food & Beverage", "Sustainable sourcing and zero food waste initiative", "2024-02-28"),
            ("Smart Building Solutions", "Real Estate", "Net-zero energy buildings and green certification for all properties", "2024-03-25"),
            ("BioPharma Green", "Healthcare", "Sustainable pharmaceutical manufacturing and waste reduction", "2024-01-18"),
            ("Renewable Materials Co", "Materials", "100% recycled and biodegradable product portfolio", "2024-05-01"),
            ("EcoConsulting Group", "Consulting", "Help 500+ companies achieve sustainability goals and carbon neutrality", "2024-02-15"),
            ("Green Finance Bank", "Finance", "Carbon-neutral operations and sustainable investment portfolio", "2024-04-05"),
            ("Sustainable Fashion House", "Fashion", "Ethical sourcing and zero-waste fashion production", "2024-03-20"),
            ("CleanTech Innovations", "Technology", "Develop and deploy clean technology solutions globally", "2024-01-25"),
            ("EcoHospitality Group", "Hospitality", "Sustainable tourism and carbon-offset travel experiences", "2024-02-10"),
            ("Green Education Institute", "Education", "Carbon-neutral campus and sustainability education programs", "2024-04-18")
        ]
        
        # Insert organizations
        insert_query = """
        INSERT INTO Organizations (name, industry, sustainability_goal, registration_date)
        VALUES (%s, %s, %s, %s)
        """
        
        cursor.executemany(insert_query, organizations)
        connection.commit()
        
        print(f"✓ Successfully seeded {cursor.rowcount} organizations!")
        
        # Display inserted organizations
        cursor.execute("SELECT org_id, name, industry FROM Organizations ORDER BY org_id")
        results = cursor.fetchall()
        
        print("\nOrganizations in database:")
        print("-" * 80)
        for org in results:
            print(f"ID: {org[0]:3d} | {org[1]:35s} | {org[2]}")
        print("-" * 80)
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as err:
        print(f"✗ Database error: {err}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    print("Seeding Organizations table...")
    print("=" * 80)
    seed_organizations()

initial = l[0]
for i in l:
    if 
    