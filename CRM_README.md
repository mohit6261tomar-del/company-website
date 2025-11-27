# Kodeminds CRM System

A comprehensive Customer Relationship Management (CRM) system built with Flask, SQLAlchemy, and Bootstrap 5.

## Features

### 1. Admin Panel
- **Dashboard**: View statistics, lead distribution, staff performance, and analytics
- **Add Leads**: Form to add new leads with all required fields
- **Analytics**: Detailed reports with charts and graphs
- **Message Templates**: Create and manage SMS/WhatsApp/Email templates
- **Audit Logs**: Track all system activities
- **Bulk Operations**: Import/Export leads via CSV

### 2. Marketing Staff Portal
- **Separate Login**: Phone number + password authentication
- **Lead Management Dashboard**: View, search, filter, and sort leads
- **Lead Details Page**: Complete lead information with activity history
- **Quick Actions**:
  - Call Lead (tel: link)
  - WhatsApp Lead (with auto-generated message)
  - SMS Lead (with auto-generated message)
  - Email Lead
- **Add Notes**: Comment on leads
- **Update Status**: Change lead status (New, Contacted, In Progress, Won, Lost)
- **Activity Tracking**: All interactions are logged

### 3. Lead Management
- **Fields**:
  - Lead Name (optional)
  - Business Name (required)
  - Phone Number (required)
  - Email (optional)
  - Business Address (required)
  - Status, Priority, Source
  - Assigned Staff
  - Follow-up Date
- **Search & Filter**: By name, business, phone, status, assigned staff
- **Sorting**: By date, name, status
- **Delete Leads**: With confirmation

### 4. Communication Features
- **Auto-generated Messages**: Dynamic message templates with placeholders
- **Message Preview**: See message before sending
- **Activity Logging**: Track all calls, WhatsApp, SMS, emails
- **Message Templates**: Predefined templates for quick communication

### 5. Analytics & Reporting
- **Lead Statistics**: Total, new, contacted, in progress, won, lost
- **Status Distribution**: Pie charts and tables
- **Staff Performance**: Leads handled, contacted, converted
- **Conversion Rate**: Track success metrics
- **Time-based Reports**: Day, week, month views
- **Exportable Reports**: CSV export for Excel/Google Sheets

### 6. Security & Audit
- **Password Hashing**: Bcrypt encryption
- **Separate Sessions**: Admin and staff have separate authentication
- **Audit Logs**: Track all actions (create, update, delete, view)
- **IP Tracking**: Log IP addresses for security
- **Role-based Access**: Admin vs Staff permissions

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python init_crm_db.py
```

This will:
- Create all database tables
- Create default admin user
- Create sample marketing staff
- Create sample leads
- Create default message templates

### 3. Run the Application
```bash
python run.py
```

## Default Credentials

### CRM Landing Page
- URL: http://localhost:5000/crm
- Choose between Admin or Staff login

### Main Admin Login (redirects to CRM)
- URL: http://localhost:5000/admin/login
- Username: `kodemindscrm`
- Password: `kodeminds97`
- **Access**: Redirects to CRM landing page
- **Note**: This is the main admin login that redirects to CRM

### CRM Admin Login
- URL: http://localhost:5000/crm/admin/login
- Username: `crmadmin`
- Password: `crm123`
- **Access**: Full CRM system with analytics, templates, audit logs

## Authentication & Security

The CRM system uses a **secure, layered authentication** approach:

1. **Separate Sessions**: Admin and staff use different authentication methods
   - Admin: Flask-Login (User model)
   - Staff: Custom session (MarketingStaff model)

2. **Role-Based Access Control**: 
   - Decorators protect routes (`@crm_admin_required`, `@staff_login_required`)
   - Each user type can only access their designated areas

3. **Security Features**:
   - Bcrypt password hashing
   - CSRF protection on all forms
   - Audit logging for all actions
   - IP address tracking
   - Session timeout
   - Account activation status check

4. **Error Handling**:
   - Graceful redirects for unauthorized access
   - Flash messages for user feedback
   - Failed login attempt logging

For detailed authentication documentation, see `AUTHENTICATION_GUIDE.md`

## Usage Guide

### For Admins

1. **Login** at `/crm/admin/login`
2. **View Dashboard** - See all statistics and recent leads
3. **Add Lead** - Click "Add Lead" button
   - Fill in business name, phone, address (required)
   - Optionally add lead name, email
   - Set status, priority, source
   - Assign to marketing staff
   - Set follow-up date
4. **View Analytics** - Click "Analytics" to see detailed reports
5. **Manage Templates** - Create message templates for staff
6. **Export Leads** - Download all leads as CSV
7. **Import Leads** - Upload CSV file to bulk import
8. **View Audit Logs** - Track all system activities

### For Marketing Staff

1. **Register** at `/crm/staff/register` (first time)
2. **Login** at `/crm/staff/login`
3. **View Dashboard** - See all leads in table format
4. **Search Leads** - Use search box to find by name/business/phone
5. **Filter Leads** - Filter by status (New, Contacted, etc.)
6. **Sort Leads** - Sort by date, name, or status
7. **View Lead Details** - Click on any lead to see full information
8. **Quick Actions**:
   - **Call**: Click phone icon to call
   - **WhatsApp**: Click WhatsApp icon (opens with pre-filled message)
   - **SMS**: Click SMS icon (opens with pre-filled message)
   - **Email**: Click email icon
9. **Add Notes** - Add comments/notes to leads
10. **Update Status** - Change lead status as you progress
11. **Edit Lead** - Update lead information
12. **Delete Lead** - Remove lead (with confirmation)

### Auto-generated Message Format

When you click WhatsApp or SMS, the following message is automatically generated:

```
Hello [Lead Name or Business Name],

My name is [Staff Name] from Kodeminds Software Solution.

We provide all kinds of software-related services including website and business management software for [Business Name].

Please contact us at +918458804893 or visit our website https://kodeminds.com
```

## Database Models

### Lead
- Basic info: lead_name, business_name, phone, email, address
- Status: new, contacted, in_progress, won, lost
- Priority: low, medium, high
- Assignment: assigned_to (staff)
- Tracking: follow_up_date, last_contacted
- Timestamps: created_at, updated_at

### MarketingStaff
- Authentication: phone_number, password_hash
- Profile: name, email
- Status: is_active
- Tracking: last_seen

### LeadNote
- Relationship: lead_id, staff_id
- Content: note
- Timestamp: created_at

### LeadActivity
- Relationship: lead_id, staff_id
- Type: call, whatsapp, sms, email, status_change, note_added
- Content: description
- Timestamp: created_at

### MessageTemplate
- Template: name, template_type, subject, content
- Status: is_active

### AuditLog
- User: user_type, user_id
- Action: action, entity_type, entity_id
- Details: description, ip_address
- Timestamp: created_at

## API Endpoints

### Admin Routes
- `GET/POST /crm/admin/login` - Admin login
- `GET /crm/admin/dashboard` - Admin dashboard
- `GET/POST /crm/admin/add-lead` - Add new lead
- `GET /crm/admin/analytics` - Analytics dashboard
- `GET /crm/admin/templates` - Message templates
- `GET/POST /crm/admin/templates/add` - Add template
- `GET /crm/admin/audit-logs` - Audit logs
- `GET /crm/admin/leads/export` - Export leads CSV
- `POST /crm/admin/leads/import` - Import leads CSV

### Staff Routes
- `GET/POST /crm/staff/login` - Staff login
- `GET/POST /crm/staff/register` - Staff registration
- `GET /crm/staff/logout` - Staff logout
- `GET /crm/staff/dashboard` - Staff dashboard
- `GET /crm/staff/lead/<id>` - View lead details
- `POST /crm/staff/lead/<id>/add-note` - Add note to lead
- `POST /crm/staff/lead/<id>/update-status` - Update lead status
- `POST /crm/staff/lead/<id>/log-activity` - Log activity
- `POST /crm/staff/lead/<id>/delete` - Delete lead
- `GET/POST /crm/staff/lead/<id>/edit` - Edit lead

## Technologies Used

- **Backend**: Flask, SQLAlchemy, Flask-Login, Flask-WTF
- **Database**: SQLite (can be changed to PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5, Font Awesome, Chart.js
- **Security**: Bcrypt password hashing, CSRF protection
- **Forms**: WTForms with validation

## Customization

### Change Company Details
Edit the message template in `app/crm/routes.py` in the `staff_view_lead` function:
```python
message = f"Hello {lead_display_name},\n\n"
message += f"My name is {staff.name} from YOUR COMPANY NAME.\n\n"
message += f"YOUR SERVICES DESCRIPTION.\n\n"
message += "Please contact us at YOUR_PHONE or visit YOUR_WEBSITE"
```

### Add More Lead Fields
1. Add column to `Lead` model in `app/models.py`
2. Add field to forms in `app/crm/forms.py`
3. Update templates to display new field

### Customize Message Templates
Login as admin and go to Message Templates to create custom templates.

## Troubleshooting

### Database Errors
```bash
# Reset database
rm instance/site.db
python init_crm_db.py
```

### Import Errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Login Issues
- CRM Admin: Use username `crmadmin` and password `crm123`
- Main Admin Panel: Use username `admin` and password `admin123`
- Staff: Use phone number format `+919876543210`

## Future Enhancements (Optional)

- [ ] Dark/Light mode toggle
- [ ] Real-time notifications
- [ ] Email integration (SMTP)
- [ ] SMS API integration
- [ ] WhatsApp Business API
- [ ] AI-powered lead scoring
- [ ] Automated follow-up reminders
- [ ] Mobile app (PWA)
- [ ] Two-factor authentication
- [ ] Advanced reporting (PDF export)
- [ ] Lead assignment automation
- [ ] Calendar integration
- [ ] Task management
- [ ] Pipeline visualization

## Support

For issues or questions, contact: support@kodeminds.com

## License

Proprietary - Kodeminds Software Solution

---

**Kodeminds CRM System v1.0**
Built with ❤️ by Kodeminds Software Solution
