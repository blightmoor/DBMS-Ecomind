# Admin Panel Documentation

## Overview
The Admin Panel provides comprehensive user management capabilities for EcoMind administrators.

## Features

### 1. User Management
- **View All Users**: See complete list of registered users with their details
- **Search & Filter**: Search by name/email and filter by status (pending/approved/rejected) and role (user/admin)
- **User Actions**:
  - Approve/Reject user registrations
  - Promote users to admin or demote to regular user
  - Delete users (except your own account)

### 2. Dashboard Statistics
- **Total Users**: Count of all registered users
- **Pending**: Users awaiting approval
- **Approved**: Active approved users
- **Rejected**: Rejected user accounts
- **Admins**: Count of admin users

### 3. Security
- **Role-Based Access**: Only users with `role='admin'` can access the admin panel
- **Route Protection**: Automatic redirect to login if not authenticated or to home if not admin
- **Self-Protection**: Admins cannot delete their own accounts

## Database Schema

```sql
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    org_id INT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES Organizations(org_id)
);
```

## API Endpoints

### Get All Users
```http
GET /api/admin/users?admin_id={admin_id}
```
Returns list of all users with their details.

### Update User Status
```http
PUT /api/admin/users/status?admin_id={admin_id}
Content-Type: application/json

{
  "user_id": 123,
  "status": "approved" | "rejected" | "pending"
}
```

### Update User Role
```http
PUT /api/admin/users/role?admin_id={admin_id}
Content-Type: application/json

{
  "user_id": 123,
  "role": "admin" | "user"
}
```

### Delete User
```http
DELETE /api/admin/users/{user_id}?admin_id={admin_id}
```

## Access Control

### Creating an Admin User
To create your first admin user, you need to:

1. Register a normal user account through the signup page
2. Manually update the database to set `role='admin'`:
```sql
UPDATE Users SET role='admin', status='approved' WHERE email='admin@example.com';
```

OR create directly via SQL:
```sql
INSERT INTO Users (name, email, password_hash, role, status)
VALUES (
    'Admin User',
    'admin@example.com',
    SHA2('your_password', 256),
    'admin',
    'approved'
);
```

### Testing Admin Access
1. Login with an admin account
2. You'll see "Admin Panel" link in the sidebar (with Shield icon)
3. Click to access the admin dashboard
4. Non-admin users will not see this link and will be redirected if they try to access `/admin`

## Usage Examples

### Approve Multiple Pending Users
1. Set filter to "Pending" status
2. Click the green checkmark (Approve) button for each user
3. Users will move to "Approved" status

### Promote User to Admin
1. Find the user in the table
2. Change their role dropdown from "User" to "Admin"
3. Change is saved immediately

### Search for Specific User
1. Type name or email in the search box
2. Results filter in real-time
3. Combine with status/role filters for more specific results

## Security Best Practices

1. **Limit Admin Accounts**: Only create admin accounts for trusted users
2. **Regular Audits**: Periodically review user list for suspicious accounts
3. **Status Management**: Keep pending users list manageable by regularly approving/rejecting
4. **Backup Before Deletion**: Always confirm before deleting users as this action is irreversible

## Troubleshooting

### "Access Denied" Message
- Ensure your account has `role='admin'` in the database
- Check that you're logged in
- Clear browser cache and sessionStorage if needed

### Users Not Loading
- Check backend is running: `uvicorn main:app --reload`
- Verify database connection in `.env` file
- Check browser console for API errors

### Cannot Delete User
- You cannot delete your own admin account
- Ensure user_id is valid
- Check database foreign key constraints

## Future Enhancements

Potential features for future development:
- Bulk actions (approve/reject multiple users at once)
- Export user list to CSV
- User activity logs
- Email notifications for status changes
- Advanced permissions and role hierarchy
- User profile editing from admin panel
- Organization management
- System settings configuration
