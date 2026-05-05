# uvicorn main:app --reload --host 0.0.0.0 --port 8000
from fastapi import FastAPI, Query, HTTPException, Request
import mysql.connector
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime
import hashlib

load_dotenv()

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or set to your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class LoginRequest(BaseModel):
    username: str  # Can be email or name
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user_data: Optional[dict] = None

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"
    org_id: Optional[int] = None  # Required for users, optional for validation

class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[int] = None
    status: Optional[str] = None

# Database connection
def get_connection():
    # Check if all required environment variables are set
    required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),  # Default to 3306 if not set
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
    except mysql.connector.Error as err:
        raise Exception(f"Failed to connect to database: {err}")

# Helper function to hash password with SHA-256
def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Helper function to log actions to AuditLogs table
def log_action(user_id: Optional[int], action: str, details: str):
    """
    Log user actions to the AuditLogs table
    - user_id: ID of the user performing the action (can be None for system actions)
    - action: Type of action (e.g., 'LOGIN', 'INSERT', 'UPDATE', 'DELETE', 'SELECT')
    - details: Additional details about the action
    """
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO AuditLogs (user_id, action, details, timestamp)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """
        cursor.execute(insert_query, (user_id, action, details))
        connection.commit()
        
        cursor.close()
        connection.close()
    except Exception as e:
        # Don't fail the main operation if logging fails
        print(f"Failed to log action: {e}")

# Login endpoint
@app.post("/api/login", response_model=LoginResponse)
def login(login_data: LoginRequest):
    """
    Authenticate user with username/email and password
    """
    try:
        # Establish database connection
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Hash the provided password
        hashed_password = hash_password(login_data.password)
        
        # Query to find user by email or name and verify password
        query = """
        SELECT user_id, name, email, org_id, 
               created_at, role, status 
        FROM Users 
        WHERE (email = %s OR name = %s) AND password_hash = %s
        """
        cursor.execute(query, (login_data.username, login_data.username, hashed_password))
        
        # Fetch user data
        user = cursor.fetchone()
        
        # Close connections
        cursor.close()
        connection.close()
        
        if user:
            # Login successful
            log_action(user["user_id"], "LOGIN", f"User {user['name']} logged in successfully")
            return LoginResponse(
                success=True,
                message="Login successful",
                user_data={
                    "user_id": user["user_id"],
                    "name": user["name"],
                    "email": user["email"],
                    "org_id": user["org_id"],
                    "created_at": str(user["created_at"]),
                    "role": user["role"],
                    "status": user["status"]
                }
            )
        else:
            # Login failed
            log_action(None, "LOGIN_FAILED", f"Failed login attempt for username: {login_data.username}")
            return LoginResponse(
                success=False,
                message="Invalid username or password"
            )
        
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Get all organizations endpoint
@app.get("/api/organizations")
def get_organizations():
    """
    Get list of all organizations for registration dropdown
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT org_id, name, industry
        FROM Organizations
        ORDER BY name ASC
        """
        cursor.execute(query)
        organizations = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "organizations": organizations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Registration endpoint
@app.post("/api/register", response_model=RegisterResponse)
def register(register_data: RegisterRequest):
    """
    Register a new user in the database
    User must select an organization (org_id is required)
    Status defaults to 'pending' - admin approval required
    """
    try:
        # Establish database connection
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Validate that org_id is provided
        if not register_data.org_id:
            cursor.close()
            connection.close()
            return RegisterResponse(
                success=False,
                message="Organization selection is required"
            )
        
        # Verify organization exists
        cursor.execute("SELECT org_id, name FROM Organizations WHERE org_id = %s", (register_data.org_id,))
        organization = cursor.fetchone()
        
        if not organization:
            cursor.close()
            connection.close()
            return RegisterResponse(
                success=False,
                message="Selected organization does not exist"
            )
        
        # Check if email already exists
        check_query = "SELECT email FROM Users WHERE email = %s"
        cursor.execute(check_query, (register_data.email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            connection.close()
            return RegisterResponse(
                success=False,
                message="Email already registered"
            )
        
        # Hash the password
        hashed_password = hash_password(register_data.password)
        
        # Insert new user with pending status
        insert_query = """
        INSERT INTO Users (name, email, password_hash, role, org_id, status, created_at)
        VALUES (%s, %s, %s, %s, %s, 'pending', CURRENT_TIMESTAMP)
        """
        cursor.execute(insert_query, (
            register_data.name,
            register_data.email,
            hashed_password,
            'user',  # Always register as 'user', admin promotes later
            register_data.org_id
        ))
        
        # Get the inserted user ID
        user_id = cursor.lastrowid
        
        # Commit the transaction
        connection.commit()
        
        # Log the registration
        log_action(user_id, "REGISTER", f"New user registered: {register_data.name} ({register_data.email}) for organization: {organization['name']}")
        
        # Close connections
        cursor.close()
        connection.close()
        
        return RegisterResponse(
            success=True,
            message="Registration successful! Your account is pending admin approval.",
            user_id=user_id,
            status="pending"
        )
        
    except mysql.connector.Error as err:
        # Rollback in case of error
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except Exception as e:
        # Rollback in case of error
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Admin endpoints

class UserStatusUpdate(BaseModel):
    user_id: int
    status: str  # 'approved', 'rejected', 'pending'

class UserRoleUpdate(BaseModel):
    user_id: int
    role: str  # 'admin', 'user'

@app.get("/api/admin/users")
def get_all_users(admin_id: int = Query(...)):
    """
    Get all users from the same organization (admin only)
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify admin role and get admin's org_id
        cursor.execute("SELECT role, org_id FROM Users WHERE user_id = %s", (admin_id,))
        admin = cursor.fetchone()
        
        if not admin or admin['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        admin_org_id = admin['org_id']
        
        # Get users from the same organization only
        # If admin has no org (org_id is NULL), show only users with NULL org_id
        if admin_org_id is None:
            query = """
            SELECT u.user_id, u.name, u.email, u.role, u.status, u.created_at, 
                   o.name as org_name, u.org_id
            FROM Users u
            LEFT JOIN Organizations o ON u.org_id = o.org_id
            WHERE u.org_id IS NULL
            ORDER BY u.created_at DESC
            """
            cursor.execute(query)
        else:
            query = """
            SELECT u.user_id, u.name, u.email, u.role, u.status, u.created_at, 
                   o.name as org_name, u.org_id
            FROM Users u
            LEFT JOIN Organizations o ON u.org_id = o.org_id
            WHERE u.org_id = %s
            ORDER BY u.created_at DESC
            """
            cursor.execute(query, (admin_org_id,))
        
        users = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Log the action
        log_action(admin_id, "VIEW_USERS", f"Admin viewed user list for organization")
        
        # Convert datetime to string
        for user in users:
            if user['created_at']:
                user['created_at'] = str(user['created_at'])
        
        return {"success": True, "users": users}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.put("/api/admin/users/status")
def update_user_status(status_data: UserStatusUpdate, admin_id: int = Query(...)):
    """
    Update user status (admin only, same organization)
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify admin role and get admin's org_id
        cursor.execute("SELECT role, org_id FROM Users WHERE user_id = %s", (admin_id,))
        admin = cursor.fetchone()
        
        if not admin or admin['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        admin_org_id = admin['org_id']
        
        # Verify target user is in the same organization
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (status_data.user_id,))
        target_user = cursor.fetchone()
        
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if both users are in the same org (including both being NULL)
        if admin_org_id != target_user['org_id']:
            raise HTTPException(status_code=403, detail="Access denied. Can only manage users from your organization.")
        
        # Update user status
        update_query = "UPDATE Users SET status = %s WHERE user_id = %s"
        cursor.execute(update_query, (status_data.status, status_data.user_id))
        connection.commit()
        
        # Log the action
        log_action(admin_id, "UPDATE_USER_STATUS", f"Admin updated user {status_data.user_id} status to {status_data.status}")
        
        cursor.close()
        connection.close()
        
        return {"success": True, "message": "User status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.put("/api/admin/users/role")
def update_user_role(role_data: UserRoleUpdate, admin_id: int = Query(...)):
    """
    Update user role (admin only, same organization)
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify admin role and get admin's org_id
        cursor.execute("SELECT role, org_id FROM Users WHERE user_id = %s", (admin_id,))
        admin = cursor.fetchone()
        
        if not admin or admin['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        admin_org_id = admin['org_id']
        
        # Verify target user is in the same organization
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (role_data.user_id,))
        target_user = cursor.fetchone()
        
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if both users are in the same org (including both being NULL)
        if admin_org_id != target_user['org_id']:
            raise HTTPException(status_code=403, detail="Access denied. Can only manage users from your organization.")
        
        # Update user role
        update_query = "UPDATE Users SET role = %s WHERE user_id = %s"
        cursor.execute(update_query, (role_data.role, role_data.user_id))
        connection.commit()
        
        # Log the action
        log_action(admin_id, "UPDATE_USER_ROLE", f"Admin updated user {role_data.user_id} role to {role_data.role}")
        
        cursor.close()
        connection.close()
        
        return {"success": True, "message": "User role updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, admin_id: int = Query(...)):
    """
    Delete user (admin only, same organization)
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify admin role and get admin's org_id
        cursor.execute("SELECT role, org_id FROM Users WHERE user_id = %s", (admin_id,))
        admin = cursor.fetchone()
        
        if not admin or admin['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        # Prevent admin from deleting themselves
        if user_id == admin_id:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        admin_org_id = admin['org_id']
        
        # Verify target user is in the same organization
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (user_id,))
        target_user = cursor.fetchone()
        
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if both users are in the same org (including both being NULL)
        if admin_org_id != target_user['org_id']:
            raise HTTPException(status_code=403, detail="Access denied. Can only manage users from your organization.")
        
        # Delete user
        delete_query = "DELETE FROM Users WHERE user_id = %s"
        cursor.execute(delete_query, (user_id,))
        connection.commit()
        
        # Log the action
        log_action(admin_id, "DELETE_USER", f"Admin deleted user {user_id}")
        
        cursor.close()
        connection.close()
        
        return {"success": True, "message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Dashboard endpoints

@app.get("/api/dashboard/stats")
def get_dashboard_stats(user_id: int = Query(...)):
    """
    Get dashboard statistics for user's organization
    Always shows current month data (not affected by filters)
    Comparison uses same number of days from last month
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user's org_id
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        org_id = user['org_id']
        
        if org_id is None:
            # Individual user - return empty/default stats
            return {
                "success": True,
                "stats": {
                    "total_emissions": 0,
                    "emission_reduction": 0,
                    "energy_usage": 0,
                    "offset_achieved": 0
                }
            }
        
        # Get current month's emissions (from 1st to today)
        query_current = """
        SELECT COALESCE(SUM(co2_emitted), 0) as total_emissions,
               COALESCE(SUM(energy_consumed), 0) as total_energy
        FROM DailyEmissions
        WHERE org_id = %s 
        AND MONTH(record_date) = MONTH(CURRENT_DATE()) 
        AND YEAR(record_date) = YEAR(CURRENT_DATE())
        AND DAY(record_date) <= DAY(CURRENT_DATE())
        """
        cursor.execute(query_current, (org_id,))
        current_month = cursor.fetchone()
        
        # Get last month's emissions for the same number of days
        # For example, if today is Oct 29, compare with Sep 1-29
        query_last_month = """
        SELECT COALESCE(SUM(co2_emitted), 0) as total_emissions
        FROM DailyEmissions
        WHERE org_id = %s 
        AND MONTH(record_date) = MONTH(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH))
        AND YEAR(record_date) = YEAR(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH))
        AND DAY(record_date) <= DAY(CURRENT_DATE())
        """
        cursor.execute(query_last_month, (org_id,))
        last_month = cursor.fetchone()
        
        # Calculate reduction percentage
        emission_reduction = 0
        if last_month['total_emissions'] > 0:
            emission_reduction = ((last_month['total_emissions'] - current_month['total_emissions']) 
                                / last_month['total_emissions'] * 100)
        
        # Calculate offset (simplified - 10% of emissions for demo)
        offset_achieved = current_month['total_emissions'] * 0.10
        
        cursor.close()
        connection.close()
        
        # Log the data retrieval
        log_action(user_id, "SELECT_DASHBOARD_STATS", f"User retrieved dashboard statistics")
        
        return {
            "success": True,
            "stats": {
                "total_emissions": round(current_month['total_emissions'], 2),
                "emission_reduction": round(emission_reduction, 2),
                "energy_usage": round(current_month['total_energy'], 2),
                "offset_achieved": round(offset_achieved, 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/api/dashboard/emissions-over-time")
def get_emissions_over_time(user_id: int = Query(...), filter: str = Query("monthly")):
    """
    Get emissions data over time based on filter
    Filter: daily (last 30 days), weekly (last 12 weeks), monthly (all 12 months of current year)
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user's org_id
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        org_id = user['org_id']
        
        if org_id is None:
            return {"success": True, "data": []}
        
        # Build query based on filter
        if filter == "daily":
            # Last 30 days with recursive CTE to ensure all days show up
            query = """
            WITH RECURSIVE date_range AS (
                SELECT DATE_SUB(CURDATE(), INTERVAL 29 DAY) as date
                UNION ALL
                SELECT DATE_ADD(date, INTERVAL 1 DAY)
                FROM date_range
                WHERE date < CURDATE()
            )
            SELECT 
                DATE_FORMAT(dr.date, '%d %b') as month,
                COALESCE(SUM(de.co2_emitted), 0) as emissions
            FROM date_range dr
            LEFT JOIN DailyEmissions de ON DATE(de.record_date) = dr.date AND de.org_id = %s
            GROUP BY dr.date, DATE_FORMAT(dr.date, '%d %b')
            ORDER BY dr.date ASC
            """
            cursor.execute(query, (org_id,))
        elif filter == "weekly":
            # Last 10 weeks with actual week numbers
            query = """
            WITH RECURSIVE week_range AS (
                SELECT 
                    DATE_SUB(CURDATE(), INTERVAL 9 WEEK) as week_start,
                    WEEK(DATE_SUB(CURDATE(), INTERVAL 9 WEEK), 1) as week_num
                UNION ALL
                SELECT 
                    DATE_ADD(week_start, INTERVAL 7 DAY),
                    WEEK(DATE_ADD(week_start, INTERVAL 7 DAY), 1)
                FROM week_range
                WHERE DATE_ADD(week_start, INTERVAL 7 DAY) <= CURDATE()
            )
            SELECT 
                CONCAT('W', wr.week_num) as month,
                COALESCE(SUM(de.co2_emitted), 0) as emissions
            FROM week_range wr
            LEFT JOIN DailyEmissions de ON 
                YEARWEEK(de.record_date, 1) = YEARWEEK(wr.week_start, 1)
                AND de.org_id = %s
            GROUP BY wr.week_num, wr.week_start
            ORDER BY wr.week_start ASC
            """
            cursor.execute(query, (org_id,))
        else:  # monthly - all 12 months of current year
            query = """
            WITH RECURSIVE month_range AS (
                SELECT 1 as month_num
                UNION ALL
                SELECT month_num + 1
                FROM month_range
                WHERE month_num < 12
            )
            SELECT 
                DATE_FORMAT(DATE(CONCAT(YEAR(CURDATE()), '-', LPAD(mr.month_num, 2, '0'), '-01')), '%b') as month,
                COALESCE(SUM(de.co2_emitted), 0) as emissions
            FROM month_range mr
            LEFT JOIN DailyEmissions de ON 
                MONTH(de.record_date) = mr.month_num 
                AND YEAR(de.record_date) = YEAR(CURDATE())
                AND de.org_id = %s
            GROUP BY mr.month_num
            ORDER BY mr.month_num ASC
            """
            cursor.execute(query, (org_id,))
        
        data = cursor.fetchall()
        
        # Format data
        result = [{"month": row['month'], "emissions": round(row['emissions'], 2)} for row in data]
        
        cursor.close()
        connection.close()
        
        return {"success": True, "data": result}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/api/dashboard/breakdown")
def get_emission_breakdown(user_id: int = Query(...), filter: str = Query("monthly")):
    """
    Get emission breakdown by category/scope based on filter
    Filter: daily (today), weekly (this week), monthly (this month)
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user's org_id
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        org_id = user['org_id']
        
        if org_id is None:
            return {"success": True, "data": []}
        
        # Determine date range based on filter
        if filter == "daily":
            date_condition = "DATE(de.record_date) = CURDATE()"
        elif filter == "weekly":
            date_condition = "YEARWEEK(de.record_date, 1) = YEARWEEK(CURDATE(), 1)"
        else:  # monthly
            date_condition = "MONTH(de.record_date) = MONTH(CURRENT_DATE()) AND YEAR(de.record_date) = YEAR(CURRENT_DATE())"
        
        # Get breakdown by category for current period
        query = f"""
        SELECT 
            COALESCE(ec.name, 'Unknown') as scope,
            COALESCE(SUM(de.co2_emitted), 0) as total_emissions
        FROM DailyEmissions de
        LEFT JOIN EmissionCategories ec ON de.category_id = ec.category_id
        WHERE de.org_id = %s 
        AND {date_condition}
        GROUP BY ec.name
        ORDER BY total_emissions DESC
        """
        cursor.execute(query, (org_id,))
        data = cursor.fetchall()
        
        # Calculate total for percentages
        total = sum(row['total_emissions'] for row in data)
        
        result = []
        for row in data:
            percentage = (row['total_emissions'] / total * 100) if total > 0 else 0
            result.append({
                "scope": row['scope'],
                "emissions": round(row['total_emissions'], 2),
                "percentage": round(percentage, 2)
            })
        
        cursor.close()
        connection.close()
        
        return {"success": True, "data": result}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/api/dashboard/top-categories")
def get_top_emission_categories(user_id: int = Query(...), filter: str = Query("monthly")):
    """
    Get top emission categories for recommendations based on filter
    Filter: daily (today), weekly (this week), monthly (this month)
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user's org_id
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        org_id = user['org_id']
        
        if org_id is None:
            return {"success": True, "data": []}
        
        # Determine date range based on filter
        if filter == "daily":
            date_condition = "DATE(de.record_date) = CURDATE()"
        elif filter == "weekly":
            date_condition = "YEARWEEK(de.record_date, 1) = YEARWEEK(CURDATE(), 1)"
        else:  # monthly
            date_condition = "MONTH(de.record_date) = MONTH(CURRENT_DATE()) AND YEAR(de.record_date) = YEAR(CURRENT_DATE())"
        
        # Get top 3 categories
        query = f"""
        SELECT 
            COALESCE(ec.name, 'Unknown') as category_name,
            COALESCE(SUM(de.co2_emitted), 0) as total_emissions,
            COUNT(DISTINCT de.location_id) as location_count
        FROM DailyEmissions de
        LEFT JOIN EmissionCategories ec ON de.category_id = ec.category_id
        WHERE de.org_id = %s 
        AND {date_condition}
        GROUP BY ec.category_id, ec.name
        ORDER BY total_emissions DESC
        LIMIT 3
        """
        cursor.execute(query, (org_id,))
        data = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {"success": True, "data": data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/api/emission-data/records")
def get_emission_records(
    user_id: int = Query(...), 
    start_date: str = Query(None),
    end_date: str = Query(None),
    location_ids: str = Query(None),
    category_ids: str = Query(None)
):
    """
    Get detailed emission records for the emission data page with advanced filtering
    - start_date: Beginning of date range (YYYY-MM-DD)
    - end_date: End of date range (YYYY-MM-DD)
    - location_ids: Comma-separated location IDs
    - category_ids: Comma-separated category IDs
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user's org_id
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        org_id = user['org_id']
        
        if org_id is None:
            return {
                "success": True, 
                "summary": {}, 
                "records": [], 
                "category_breakdown": [], 
                "emissions_over_time": [],
                "locations": [],
                "categories": []
            }
        
        # Default date range to last 30 days if not provided
        if not start_date:
            cursor.execute("SELECT DATE_SUB(CURDATE(), INTERVAL 30 DAY) as default_start")
            start_date = cursor.fetchone()['default_start'].strftime('%Y-%m-%d')
        
        if not end_date:
            cursor.execute("SELECT CURDATE() as default_end")
            end_date = cursor.fetchone()['default_end'].strftime('%Y-%m-%d')
        
        # Build WHERE clause dynamically
        where_conditions = ["de.org_id = %s", "de.record_date >= %s", "de.record_date <= %s"]
        params = [org_id, start_date, end_date]
        
        if location_ids:
            location_list = [int(loc_id.strip()) for loc_id in location_ids.split(',') if loc_id.strip()]
            if location_list:
                placeholders = ','.join(['%s'] * len(location_list))
                where_conditions.append(f"de.location_id IN ({placeholders})")
                params.extend(location_list)
        
        if category_ids:
            category_list = [int(cat_id.strip()) for cat_id in category_ids.split(',') if cat_id.strip()]
            if category_list:
                placeholders = ','.join(['%s'] * len(category_list))
                where_conditions.append(f"de.category_id IN ({placeholders})")
                params.extend(category_list)
        
        where_clause = " AND ".join(where_conditions)
        
        # Get summary stats
        summary_query = f"""
        SELECT 
            COALESCE(SUM(co2_emitted), 0) as total_emissions,
            COALESCE(AVG(co2_emitted), 0) as average_per_day,
            COUNT(DISTINCT record_date) as days_count
        FROM DailyEmissions de
        WHERE {where_clause}
        """
        cursor.execute(summary_query, params)
        summary = cursor.fetchone()

        # Calculate previous period for comparison (same length as current period)
        cursor.execute("SELECT DATEDIFF(%s, %s) as days_diff", (end_date, start_date))
        days_diff = cursor.fetchone()['days_diff']
        
        prev_period_query = f"""
        SELECT COALESCE(SUM(co2_emitted), 0) as prev_emissions
        FROM DailyEmissions de
        WHERE de.org_id = %s 
        AND de.record_date >= DATE_SUB(%s, INTERVAL {days_diff + 1} DAY)
        AND de.record_date < %s
        """
        cursor.execute(prev_period_query, (org_id, start_date, start_date))
        prev_period = cursor.fetchone()
        
        # Calculate change percentage
        change_from_last_period = 0
        if prev_period['prev_emissions'] > 0:
            change_from_last_period = ((summary['total_emissions'] - prev_period['prev_emissions']) / prev_period['prev_emissions'] * 100)
        
        # Get emissions over time grouped by date AND category (for multi-line chart)
        emissions_time_query = f"""
        SELECT 
            DATE(de.record_date) as date,
            COALESCE(ec.name, 'Unknown') as category,
            ec.category_id,
            COALESCE(SUM(de.co2_emitted), 0) as value
        FROM DailyEmissions de
        LEFT JOIN EmissionCategories ec ON de.category_id = ec.category_id
        WHERE {where_clause}
        GROUP BY DATE(de.record_date), ec.category_id, ec.name
        ORDER BY DATE(de.record_date) ASC, ec.name ASC
        """
        cursor.execute(emissions_time_query, params)
        emissions_over_time = cursor.fetchall()
        
        # Get category breakdown
        category_query = f"""
        SELECT 
            COALESCE(ec.name, 'Unknown') as category,
            ec.category_id,
            COALESCE(SUM(de.co2_emitted), 0) as value
        FROM DailyEmissions de
        LEFT JOIN EmissionCategories ec ON de.category_id = ec.category_id
        WHERE {where_clause}
        GROUP BY ec.category_id, ec.name
        ORDER BY value DESC
        """
        cursor.execute(category_query, params)
        category_breakdown = cursor.fetchall()
        
        # Get detailed emission records (Recent Emissions - NOT filtered, always show latest 50)
        records_query = """
        SELECT 
            de.emission_id as id,
            DATE_FORMAT(de.record_date, '%Y-%m-%d') as date,
            COALESCE(ec.name, 'Unknown') as category,
            COALESCE(l.name, 'Unknown') as source,
            de.co2_emitted as value,
            'kg CO2' as unit
        FROM DailyEmissions de
        LEFT JOIN EmissionCategories ec ON de.category_id = ec.category_id
        LEFT JOIN Locations l ON de.location_id = l.location_id
        WHERE de.org_id = %s 
        ORDER BY de.record_date DESC, de.emission_id DESC
        LIMIT 50
        """
        cursor.execute(records_query, (org_id,))
        records = cursor.fetchall()
        
        # Get available locations for this organization (for dropdown)
        locations_query = """
        SELECT location_id, name
        FROM Locations
        WHERE org_id = %s
        ORDER BY name ASC
        """
        cursor.execute(locations_query, (org_id,))
        locations = cursor.fetchall()
        
        # Get all emission categories (for multi-select)
        categories_query = """
        SELECT category_id, name
        FROM EmissionCategories
        ORDER BY name ASC
        """
        cursor.execute(categories_query)
        categories = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Log the data retrieval
        log_action(user_id, "SELECT_EMISSION_RECORDS", f"User retrieved emission records (date range: {start_date} to {end_date})")
        
        return {
            "success": True,
            "summary": {
                "total_emissions": round(summary['total_emissions'], 2),
                "average_per_day": round(summary['average_per_day'], 2),
                "change_from_last_period": round(change_from_last_period, 2)
            },
            "emissions_over_time": [
                {
                    "date": str(row['date']), 
                    "category": row['category'],
                    "category_id": row['category_id'],
                    "value": round(row['value'], 2)
                } for row in emissions_over_time
            ],
            "category_breakdown": [
                {
                    "category": row['category'], 
                    "category_id": row['category_id'],
                    "value": round(row['value'], 2)
                } for row in category_breakdown
            ],
            "records": [
                {
                    "id": row['id'], 
                    "date": row['date'], 
                    "category": row['category'], 
                    "source": row['source'], 
                    "value": round(row['value'], 2), 
                    "unit": row['unit']
                } for row in records
            ],
            "locations": [{"location_id": loc['location_id'], "name": loc['name']} for loc in locations],
            "categories": [{"category_id": cat['category_id'], "name": cat['name']} for cat in categories]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# Audit Logs endpoint (Admin only)
@app.get("/api/admin/audit-logs")
def get_audit_logs(
    admin_id: int = Query(...),
    limit: int = Query(100),
    offset: int = Query(0),
    action_filter: str = Query(None),
    user_filter: int = Query(None)
):
    """
    Get audit logs (admin only)
    - limit: Number of records to return (default 100)
    - offset: Pagination offset (default 0)
    - action_filter: Filter by action type (optional)
    - user_filter: Filter by user_id (optional)
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify admin role
        cursor.execute("SELECT role, org_id FROM Users WHERE user_id = %s", (admin_id,))
        admin = cursor.fetchone()
        
        if not admin or admin['role'] != 'admin':
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required.")
        
        admin_org_id = admin['org_id']
        
        # Build WHERE clause for filtering
        where_conditions = []
        params = []
        
        # Filter by organization - only show logs from users in the same org
        if admin_org_id is not None:
            where_conditions.append("(al.user_id IN (SELECT user_id FROM Users WHERE org_id = %s) OR al.user_id IS NULL)")
            params.append(admin_org_id)
        
        if action_filter:
            where_conditions.append("al.action LIKE %s")
            params.append(f"%{action_filter}%")
        
        if user_filter:
            where_conditions.append("al.user_id = %s")
            params.append(user_filter)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Get total count
        count_query = f"""
        SELECT COUNT(*) as total
        FROM AuditLogs al
        WHERE {where_clause}
        """
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()['total']
        
        # Get audit logs with user information
        params_with_pagination = params + [limit, offset]
        logs_query = f"""
        SELECT 
            al.log_id,
            al.user_id,
            u.name as user_name,
            u.email as user_email,
            al.action,
            al.details,
            al.timestamp
        FROM AuditLogs al
        LEFT JOIN Users u ON al.user_id = u.user_id
        WHERE {where_clause}
        ORDER BY al.timestamp DESC
        LIMIT %s OFFSET %s
        """
        cursor.execute(logs_query, params_with_pagination)
        logs = cursor.fetchall()
        
        # Get action statistics
        stats_query = f"""
        SELECT 
            al.action,
            COUNT(*) as count
        FROM AuditLogs al
        WHERE {where_clause}
        GROUP BY al.action
        ORDER BY count DESC
        """
        cursor.execute(stats_query, params)
        action_stats = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Log this action
        log_action(admin_id, "VIEW_AUDIT_LOGS", f"Admin viewed audit logs (limit: {limit}, offset: {offset})")
        
        # Convert timestamps to strings
        for log in logs:
            if log['timestamp']:
                log['timestamp'] = str(log['timestamp'])
        
        return {
            "success": True,
            "total_count": total_count,
            "logs": logs,
            "action_stats": action_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# AI Insights endpoints

@app.get("/api/ai-insights/predictions")
def get_ai_predictions(user_id: int = Query(...)):
    """
    Get AI predictions for next month's emissions, energy, and trends
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user's org_id
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        org_id = user['org_id']
        
        if org_id is None:
            raise HTTPException(status_code=400, detail="User is not associated with an organization")
        
        # Get current month's emissions and energy
        cursor.execute("""
            SELECT 
                COALESCE(SUM(co2_emitted), 0) as current_month_emissions,
                COALESCE(SUM(energy_consumed), 0) as current_month_energy
            FROM DailyEmissions
            WHERE org_id = %s 
            AND MONTH(record_date) = MONTH(CURRENT_DATE()) 
            AND YEAR(record_date) = YEAR(CURRENT_DATE())
        """, (org_id,))
        current_month = cursor.fetchone()
        
        # Get last 6 months average for prediction
        cursor.execute("""
            SELECT 
                COALESCE(AVG(monthly_emissions), 0) as avg_emissions,
                COALESCE(AVG(monthly_energy), 0) as avg_energy
            FROM (
                SELECT 
                    SUM(co2_emitted) as monthly_emissions,
                    SUM(energy_consumed) as monthly_energy
                FROM DailyEmissions
                WHERE org_id = %s 
                AND record_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
                GROUP BY YEAR(record_date), MONTH(record_date)
            ) as monthly_data
        """, (org_id,))
        avg_data = cursor.fetchone()
        
        # Simple prediction: average of last 6 months with slight downward trend
        predicted_next_month_emissions = round(avg_data['avg_emissions'] * 0.95, 2)
        predicted_next_month_energy = round(avg_data['avg_energy'] * 0.96, 2)
        
        emissions_change = round(((predicted_next_month_emissions - current_month['current_month_emissions']) / current_month['current_month_emissions'] * 100) if current_month['current_month_emissions'] > 0 else 0, 2)
        energy_change = round(((predicted_next_month_energy - current_month['current_month_energy']) / current_month['current_month_energy'] * 100) if current_month['current_month_energy'] > 0 else 0, 2)
        
        # Get top risk sources (categories with highest emissions)
        cursor.execute("""
            SELECT 
                COALESCE(ec.name, 'Unknown') as category_name,
                COALESCE(SUM(de.co2_emitted), 0) as total_emissions
            FROM DailyEmissions de
            LEFT JOIN EmissionCategories ec ON de.category_id = ec.category_id
            WHERE de.org_id = %s 
            AND de.record_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)
            GROUP BY ec.category_id, ec.name
            ORDER BY total_emissions DESC
            LIMIT 3
        """, (org_id,))
        top_risk_sources = [row['category_name'] for row in cursor.fetchall()]
        
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "predictions": {
                "next_month_emissions": {
                    "value": predicted_next_month_emissions,
                    "change": emissions_change,
                    "trend": "down" if emissions_change < 0 else "up"
                },
                "next_month_energy": {
                    "value": predicted_next_month_energy,
                    "change": energy_change,
                    "trend": "down" if energy_change < 0 else "up"
                },
                "top_risk_sources": top_risk_sources
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/api/ai-insights/trends")
def get_ai_trends(user_id: int = Query(...), data_type: str = Query("emissions")):
    """
    Get historical and predicted trends for emissions or energy
    data_type: 'emissions' or 'energy'
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user's org_id
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        org_id = user['org_id']
        
        if org_id is None:
            raise HTTPException(status_code=400, detail="User is not associated with an organization")
        
        # Determine which column to query
        data_column = "co2_emitted" if data_type == "emissions" else "energy_consumed"
        
        # Get last 6 months of actual data
        cursor.execute(f"""
            SELECT 
                YEAR(record_date) as year_val,
                MONTH(record_date) as month_num,
                COALESCE(SUM({data_column}), 0) as value
            FROM DailyEmissions
            WHERE org_id = %s 
            AND record_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
            AND record_date <= CURRENT_DATE()
            GROUP BY YEAR(record_date), MONTH(record_date)
            ORDER BY YEAR(record_date), MONTH(record_date)
        """, (org_id,))
        
        actual_data = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Month names for formatting
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        # Create trend data with actual and predicted values
        trend_data = []
        
        # Add actual data
        for row in actual_data:
            month_idx = row['month_num'] - 1  # Convert 1-12 to 0-11
            trend_data.append({
                "month": month_names[month_idx],
                "actual": round(row['value'], 2),
                "predicted": round(row['value'] * 0.98, 2)
            })
        
        # Add 3 months of future predictions
        if trend_data:
            last_value = trend_data[-1]['actual']
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            current_month = datetime.now().month  # 1-12
            
            for i in range(3):
                # Calculate next month (1-indexed)
                next_month = ((current_month - 1 + i + 1) % 12)
                predicted_value = round(last_value * (0.95 ** (i + 1)), 2)
                trend_data.append({
                    "month": month_names[next_month],
                    "actual": None,
                    "predicted": predicted_value
                })
        
        return {
            "success": True,
            "data_type": data_type,
            "trends": trend_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get("/api/ai-insights/recommendations")
def get_ai_recommendations(user_id: int = Query(...)):
    """
    Get AI-generated insights and recommendations
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user's org_id
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        org_id = user['org_id']
        
        if org_id is None:
            raise HTTPException(status_code=400, detail="User is not associated with an organization")
        
        # Get category breakdown for last 30 days
        cursor.execute("""
            SELECT 
                COALESCE(ec.name, 'Unknown') as category_name,
                COALESCE(SUM(de.co2_emitted), 0) as total_emissions,
                COUNT(*) as record_count
            FROM DailyEmissions de
            LEFT JOIN EmissionCategories ec ON de.category_id = ec.category_id
            WHERE de.org_id = %s 
            AND de.record_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
            GROUP BY ec.category_id, ec.name
            ORDER BY total_emissions DESC
        """, (org_id,))
        
        categories = cursor.fetchall()
        
        # Get total emissions
        cursor.execute("""
            SELECT COALESCE(SUM(co2_emitted), 0) as total
            FROM DailyEmissions
            WHERE org_id = %s 
            AND record_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        """, (org_id,))
        
        total_emissions = cursor.fetchone()['total']
        
        # Get comparison with previous month
        cursor.execute("""
            SELECT COALESCE(SUM(co2_emitted), 0) as prev_month
            FROM DailyEmissions
            WHERE org_id = %s 
            AND record_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 60 DAY)
            AND record_date < DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        """, (org_id,))
        
        prev_month_emissions = cursor.fetchone()['prev_month']
        
        cursor.close()
        connection.close()
        
        # Generate AI insights based on data
        insights = []
        
        # Insight 1: Highest category
        if categories and len(categories) > 0:
            top_category = categories[0]
            percentage = round((top_category['total_emissions'] / total_emissions * 100) if total_emissions > 0 else 0, 1)
            insights.append({
                "id": 1,
                "type": "alert",
                "title": f"{top_category['category_name']} Emissions Dominant",
                "message": f"Your {top_category['category_name']} emissions account for {percentage}% of total emissions. Consider targeted reduction strategies for this category.",
                "confidence": 94,
                "timestamp": "5 minutes ago",
                "severity": "high"
            })
        
        # Insight 2: Month-over-month comparison
        if prev_month_emissions > 0:
            change = round(((total_emissions - prev_month_emissions) / prev_month_emissions * 100), 1)
            if change > 10:
                insights.append({
                    "id": 2,
                    "type": "warning",
                    "title": "Emissions Increasing",
                    "message": f"Your emissions have increased by {change}% compared to last month. Review recent activities and consider implementing reduction measures.",
                    "confidence": 91,
                    "timestamp": "12 minutes ago",
                    "severity": "medium"
                })
            elif change < -10:
                insights.append({
                    "id": 2,
                    "type": "success",
                    "title": "Great Progress!",
                    "message": f"Excellent work! Your emissions have decreased by {abs(change)}% compared to last month. Keep up the sustainable practices.",
                    "confidence": 93,
                    "timestamp": "12 minutes ago",
                    "severity": "low"
                })
        
        # Insight 3: Pattern-based recommendation
        insights.append({
            "id": 3,
            "type": "opportunity",
            "title": "Optimization Opportunity Detected",
            "message": "AI analysis suggests potential for 15-20% emission reduction through operational efficiency improvements. Consider scheduling an energy audit.",
            "confidence": 87,
            "timestamp": "1 hour ago",
            "severity": "medium"
        })
        
        # Insight 4: Seasonal pattern
        insights.append({
            "id": 4,
            "type": "prediction",
            "title": "Seasonal Trend Alert",
            "message": "Historical patterns indicate typical seasonal variation during this period. Proactive measures can help maintain emission targets.",
            "confidence": 85,
            "timestamp": "2 hours ago",
            "severity": "low"
        })
        
        return {
            "success": True,
            "insights": insights,
            "total_count": len(insights)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.post("/api/ai-insights/generate")
def generate_new_insight(user_id: int = Query(...)):
    """
    Generate a new AI insight on demand
    """
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get user's org_id
        cursor.execute("SELECT org_id FROM Users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        org_id = user['org_id']
        
        if org_id is None:
            raise HTTPException(status_code=400, detail="User is not associated with an organization")
        
        # Get some random insight based on recent data
        cursor.execute("""
            SELECT 
                COALESCE(ec.name, 'Unknown') as category_name,
                COALESCE(AVG(de.co2_emitted), 0) as avg_daily
            FROM DailyEmissions de
            LEFT JOIN EmissionCategories ec ON de.category_id = ec.category_id
            WHERE de.org_id = %s 
            AND de.record_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
            GROUP BY ec.category_id, ec.name
            ORDER BY avg_daily DESC
            LIMIT 1
        """, (org_id,))
        
        top_category = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        # Generate insight
        insight = {
            "id": 999,
            "type": "prediction",
            "title": "New Pattern Identified",
            "message": f"AI detected that {top_category['category_name'] if top_category else 'your primary emission source'} shows consistent patterns. Implementing smart scheduling could reduce emissions by up to 12%.",
            "confidence": 89,
            "timestamp": "Just now",
            "severity": "medium"
        }
        
        # Log the action
        log_action(user_id, "GENERATE_AI_INSIGHT", "User generated a new AI insight")
        
        return {
            "success": True,
            "insight": insight
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

