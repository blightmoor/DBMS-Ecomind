import mysql.connector

CONFIG = dict(host='localhost', user='root', password='Ukit@2104', database='SmartCarbonDB')
org_id = 1
for days in (7,):
    print(f"Testing with days={days}, org_id={org_id}")
    db = mysql.connector.connect(**CONFIG)
    cur = db.cursor()
    try:
        q1 = f"""
        SELECT COALESCE(SUM(co2_emitted), 0) as total_emissions,
               COALESCE(AVG(co2_emitted), 0) as average_per_day,
               COUNT(DISTINCT record_date) as days_count
        FROM DailyEmissions
        WHERE org_id = %s 
          AND record_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        """
        cur.execute(q1, (org_id,))
        print('q1 ok:', cur.fetchone())

        q2 = f"""
        SELECT COALESCE(SUM(co2_emitted), 0) as prev_emissions
        FROM DailyEmissions
        WHERE org_id = %s 
          AND record_date >= DATE_SUB(CURDATE(), INTERVAL {days*2} DAY)
          AND record_date < DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        """
        cur.execute(q2, (org_id,))
        print('q2 ok:', cur.fetchone())

        q3 = f"""
        SELECT DATE(record_date) as date,
               COALESCE(SUM(co2_emitted), 0) as value
        FROM DailyEmissions
        WHERE org_id = %s 
          AND record_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        GROUP BY DATE(record_date)
        ORDER BY DATE(record_date) ASC
        """
        cur.execute(q3, (org_id,))
        print('q3 rows:', cur.rowcount)

        q4 = f"""
        SELECT COALESCE(ec.name, 'Unknown') as category,
               COALESCE(SUM(de.co2_emitted), 0) as value
        FROM DailyEmissions de
        LEFT JOIN EmissionCategories ec ON de.category_id = ec.category_id
        WHERE de.org_id = %s 
          AND de.record_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        GROUP BY ec.category_id, ec.name
        ORDER BY value DESC
        """
        cur.execute(q4, (org_id,))
        print('q4 rows:', cur.rowcount)

        q5 = f"""
        SELECT de.emission_id as id,
               DATE_FORMAT(de.record_date, '%Y-%m-%d') as date,
               COALESCE(ec.name, 'Unknown') as category,
               COALESCE(l.name, 'Unknown') as source,
               de.co2_emitted as value,
               'kg CO2' as unit
        FROM DailyEmissions de
        LEFT JOIN EmissionCategories ec ON de.category_id = ec.category_id
        LEFT JOIN Locations l ON de.location_id = l.location_id
        WHERE de.org_id = %s 
          AND de.record_date >= DATE_SUB(CURDATE(), INTERVAL {days} DAY)
        ORDER BY de.record_date DESC, de.emission_id DESC
        LIMIT 5
        """
        cur.execute(q5, (org_id,))
        print('q5 rows:', cur.rowcount)
    except Exception as e:
        print('ERROR:', type(e).__name__, e)
    finally:
        cur.close(); db.close()
