# Quick Start Guide - Kodeminds CRM

## Step 1: Initialize the Database

Run the initialization script to set up the CRM database:

```bash
python init_crm_db.py
```

This creates:
- ✓ All database tables
- ✓ Admin user (admin/admin123)
- ✓ Sample marketing staff
- ✓ Sample leads
- ✓ Default message templates

## Step 2: Start the Application

```bash
python run.py
```

The application will start at: http://localhost:5000

## Step 3: Access the CRM

### CRM Admin Panel
1. Go to: http://localhost:5000/crm/admin/login
2. Login with:
   - Username: `crmadmin`
   - Password: `crm123`
3. You'll see the CRM Dashboard with:
   - Lead statistics
   - Charts and graphs
   - Recent leads table
   - Staff performance

**Note:** This is separate from the main admin panel (http://localhost:5000/admin) which uses admin/admin123

### Marketing Staff Panel
1. Go to: http://localhost:5000/crm/staff/login
2. Login with:
   - Phone: `+919876543210`
   - Password: `staff123`
3. You'll see the Lead Management Dashboard

## Step 4: Try Key Features

### As Admin:
1. **Add a Lead**: Click "Add Lead" button
   - Fill in Business Name, Phone, Address (required)
   - Assign to a staff member
   - Click "Add Lead"

2. **View Analytics**: Click "Analytics" in sidebar
   - See conversion rates
   - View staff performance
   - Check status distribution

3. **Export Leads**: Scroll to bottom of dashboard
   - Click "Export to CSV"
   - Download all leads

### As Marketing Staff:
1. **View Lead**: Click on any lead in the table
   - See all lead information
   - View notes and activity history

2. **Call Lead**: Click the phone icon
   - Opens dialer with lead's number

3. **WhatsApp Lead**: Click WhatsApp icon
   - Opens WhatsApp with pre-filled message:
   ```
   Hello [Lead Name],
   My name is [Your Name] from Kodeminds Software Solution.
   We provide all kinds of software-related services...
   ```

4. **Add Note**: In lead detail page
   - Type your note in the text area
   - Click "Add Note"

5. **Update Status**: In lead detail page
   - Select new status from dropdown
   - Click "Update Status"

6. **Search Leads**: In dashboard
   - Type name/business/phone in search box
   - Select status filter
   - Choose sort order
   - Click "Search"

## Step 5: Register New Staff

1. Go to: http://localhost:5000/crm/staff/register
2. Fill in:
   - Full Name
   - Phone Number (unique)
   - Email (optional)
   - Password (min 8 characters)
3. Click "Register"
4. Login with your phone number and password

## Common Tasks

### Add Multiple Leads via CSV
1. Login as admin
2. Prepare CSV file with columns:
   ```
   Lead Name,Business Name,Phone,Email,Address,Status,Priority,Source
   ```
3. Scroll to "Bulk Operations" section
4. Click "Choose File" and select your CSV
5. Click "Import"

### Create Message Template
1. Login as admin
2. Click "Message Templates" in sidebar
3. Click "Add Template"
4. Fill in:
   - Template Name
   - Type (SMS/WhatsApp/Email)
   - Subject (for email)
   - Message Content
5. Click "Save Template"

### View Activity Logs
1. Login as admin
2. Click "Audit Logs" in sidebar
3. See all system activities:
   - Who logged in/out
   - Leads created/updated/deleted
   - Status changes
   - Notes added

## Tips

- **Phone Format**: Use international format (+91 for India)
- **Status Workflow**: New → Contacted → In Progress → Won/Lost
- **Priority Levels**: High (urgent), Medium (normal), Low (can wait)
- **Follow-up Dates**: Set reminders for future contact
- **Notes**: Add detailed notes for each interaction
- **Activity Tracking**: All calls/messages are automatically logged

## Troubleshooting

### Can't Login?
- CRM Admin: Use `crmadmin` (not email) as username, password: `crm123`
- Main Admin Panel: Use `admin` as username, password: `admin123`
- Staff: Use phone number with country code (+91...)

### Database Error?
```bash
# Reset and reinitialize
rm instance/site.db
python init_crm_db.py
```

### Import Not Working?
- Check CSV format matches example
- Ensure phone numbers are valid
- Business Name and Address are required

## Next Steps

1. **Change Admin Password**: 
   - Login as admin
   - Update password in profile

2. **Add Real Staff**:
   - Have staff register at /crm/staff/register
   - Or create via admin panel

3. **Import Your Leads**:
   - Export from existing system
   - Format as CSV
   - Import via admin panel

4. **Customize Messages**:
   - Edit message text in lead_view template
   - Or create templates in admin panel

5. **Train Your Team**:
   - Show staff how to use dashboard
   - Explain lead workflow
   - Demonstrate quick actions

## Support

Need help? Check CRM_README.md for detailed documentation.

---

**Happy CRM-ing! 🚀**
