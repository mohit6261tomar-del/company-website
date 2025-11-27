import os
import csv
import io
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, send_file, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from wtforms.validators import Optional
from sqlalchemy import or_, func, desc, asc, case
from urllib.parse import quote
from app import db
from app.crm import bp
from app.models import (User, Lead, MarketingStaff, LeadNote, LeadActivity, 
                        MessageTemplate, AuditLog)
from app.crm.forms import (CRMAdminLoginForm, MarketingStaffLoginForm, 
                           MarketingStaffRegistrationForm, AddLeadForm, 
                           EditLeadForm, LeadNoteForm, MessageTemplateForm, SearchLeadForm,
                           StaffManagementForm, BulkAssignLeadsForm)
from app.crm.decorators import crm_admin_required, staff_login_required, prevent_staff_access


def log_audit(user_type, user_id, action, entity_type, entity_id=None, description=None):
    """Helper function to log audit trail"""
    try:
        audit = AuditLog(
            user_type=user_type,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error logging audit: {e}")


def log_lead_activity(lead_id, staff_id, activity_type, description=None):
    """Helper function to log lead activity"""
    try:
        activity = LeadActivity(
            lead_id=lead_id,
            staff_id=staff_id,
            activity_type=activity_type,
            description=description
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error logging activity: {e}")


# ============= CRM Landing Page =============

@bp.route('/')
@bp.route('/index')
def index():
    """CRM landing page - choose admin or staff login"""
    # If admin is logged in, redirect to admin dashboard
    if current_user.is_authenticated and hasattr(current_user, 'is_admin') and current_user.is_admin:
        return redirect(url_for('crm.admin_dashboard'))
    
    # If staff is logged in, redirect to staff dashboard
    if 'staff_id' in session:
        return redirect(url_for('crm.staff_dashboard'))
    
    return render_template('crm/index.html', title='Kodeminds CRM')


# ============= CRM Admin Routes =============

@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """CRM Admin login - separate from marketing staff"""
    # Clear any staff session
    if 'staff_id' in session:
        session.pop('staff_id', None)
        session.pop('staff_name', None)
    
    # If already logged in as admin, redirect to dashboard
    if current_user.is_authenticated and hasattr(current_user, 'is_admin') and current_user.is_admin:
        return redirect(url_for('crm.admin_dashboard'))
    
    form = CRMAdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.is_admin and user.check_password(form.password.data):
            # Login via Flask-Login
            login_user(user, remember=form.remember_me.data)
            log_audit('admin', user.id, 'login', 'session', description='Admin logged into CRM')
            
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('crm.admin_dashboard'))
        else:
            flash('Invalid username or password. Please check your credentials.', 'danger')
            log_audit('admin', 0, 'failed_login', 'session', description=f'Failed login attempt for {form.username.data}')
    
    return render_template('crm/admin_login.html', form=form, title='CRM Admin Login')


@bp.route('/admin/dashboard')
@crm_admin_required
def admin_dashboard():
    """CRM Admin Dashboard - requires admin authentication"""
    
    # Statistics
    total_leads = Lead.query.count()
    new_leads = Lead.query.filter_by(status='new').count()
    contacted_leads = Lead.query.filter_by(status='contacted').count()
    in_progress_leads = Lead.query.filter_by(status='in_progress').count()
    won_leads = Lead.query.filter_by(status='won').count()
    lost_leads = Lead.query.filter_by(status='lost').count()
    
    # Recent leads
    recent_leads = Lead.query.order_by(Lead.created_at.desc()).limit(10).all()
    
    # Leads by status
    status_distribution = {
        'new': new_leads,
        'contacted': contacted_leads,
        'in_progress': in_progress_leads,
        'won': won_leads,
        'lost': lost_leads
    }
    
    # Marketing staff performance
    staff_performance = db.session.query(
        MarketingStaff.name,
        func.count(Lead.id).label('total_leads'),
        func.sum(case((Lead.status == 'won', 1), else_=0)).label('converted_leads')
    ).outerjoin(Lead, MarketingStaff.id == Lead.assigned_to)\
     .group_by(MarketingStaff.id)\
     .all()
    
    # Leads added per day (last 7 days)
    today = datetime.utcnow().date()
    leads_per_day = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = Lead.query.filter(
            func.date(Lead.created_at) == date
        ).count()
        leads_per_day.append({'date': date.strftime('%Y-%m-%d'), 'count': count})
    
    return render_template('crm/admin_dashboard.html',
                         title='Kodeminds CRM Dashboard',
                         total_leads=total_leads,
                         new_leads=new_leads,
                         contacted_leads=contacted_leads,
                         in_progress_leads=in_progress_leads,
                         won_leads=won_leads,
                         lost_leads=lost_leads,
                         recent_leads=recent_leads,
                         status_distribution=status_distribution,
                         staff_performance=staff_performance,
                         leads_per_day=leads_per_day)


@bp.route('/admin/add-lead', methods=['GET', 'POST'])
@crm_admin_required
def admin_add_lead():
    """Admin add lead - requires admin authentication"""
    form = AddLeadForm()
    
    # Populate staff choices
    staff_list = MarketingStaff.query.filter_by(is_active=True).all()
    form.assigned_to.choices = [(0, 'Unassigned')] + [(s.id, s.name) for s in staff_list]
    
    if form.validate_on_submit():
        lead = Lead(
            lead_name=form.lead_name.data,
            business_name=form.business_name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            business_address=form.business_address.data,
            status=form.status.data,
            priority=form.priority.data,
            source=form.source.data,
            assigned_to=form.assigned_to.data if form.assigned_to.data != 0 else None,
            follow_up_date=form.follow_up_date.data,
            created_by_admin=current_user.id
        )
        
        try:
            db.session.add(lead)
            db.session.commit()
            
            # Log activity
            log_audit('admin', current_user.id, 'created', 'lead', lead.id, 
                     f'Created lead: {lead.business_name}')
            log_lead_activity(lead.id, None, 'created', f'Lead created by admin')
            
            flash('Lead added successfully!', 'success')
            return redirect(url_for('crm.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding lead: {e}")
            flash('Error adding lead. Please try again.', 'danger')
    
    return render_template('crm/add_lead.html', form=form, title='Add Lead')


@bp.route('/admin/analytics')
@crm_admin_required
def admin_analytics():
    """Analytics dashboard for admin - requires admin authentication"""
    # Date range filters
    period = request.args.get('period', 'week')  # day, week, month
    
    if period == 'day':
        start_date = datetime.utcnow() - timedelta(days=1)
    elif period == 'month':
        start_date = datetime.utcnow() - timedelta(days=30)
    else:  # week
        start_date = datetime.utcnow() - timedelta(days=7)
    
    # Leads added in period
    leads_in_period = Lead.query.filter(Lead.created_at >= start_date).all()
    
    # Status distribution
    status_counts = db.session.query(
        Lead.status,
        func.count(Lead.id)
    ).filter(Lead.created_at >= start_date)\
     .group_by(Lead.status)\
     .all()
    
    # Staff performance
    staff_stats = db.session.query(
        MarketingStaff.name,
        func.count(Lead.id).label('total'),
        func.sum(case((Lead.status == 'contacted', 1), else_=0)).label('contacted'),
        func.sum(case((Lead.status == 'won', 1), else_=0)).label('converted')
    ).outerjoin(Lead, MarketingStaff.id == Lead.assigned_to)\
     .filter(Lead.created_at >= start_date)\
     .group_by(MarketingStaff.id)\
     .all()
    
    # Conversion rate
    total_leads = len(leads_in_period)
    won_leads = sum(1 for lead in leads_in_period if lead.status == 'won')
    conversion_rate = (won_leads / total_leads * 100) if total_leads > 0 else 0
    
    return render_template('crm/analytics_dashboard.html',
                         title='CRM Analytics',
                         period=period,
                         total_leads=total_leads,
                         status_counts=status_counts,
                         staff_stats=staff_stats,
                         conversion_rate=conversion_rate,
                         leads_in_period=leads_in_period)


# ============= Staff Management =============

@bp.route('/admin/staff')
@crm_admin_required
def admin_staff():
    """Manage marketing staff - requires admin authentication"""
    staff_list = MarketingStaff.query.order_by(MarketingStaff.created_at.desc()).all()
    return render_template('crm/staff_list.html', staff_list=staff_list, title='Staff Management')


@bp.route('/admin/staff/add', methods=['GET', 'POST'])
@crm_admin_required
def admin_add_staff():
    """Add new marketing staff - requires admin authentication"""
    form = StaffManagementForm()

    if form.validate_on_submit():
        staff = MarketingStaff(
            name=form.name.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            is_active=form.is_active.data
        )
        staff.set_password(form.password.data)

        try:
            db.session.add(staff)
            db.session.commit()

            # Log activity
            log_audit('admin', current_user.id, 'created', 'staff', staff.id,
                     f'Created staff account: {staff.name}')

            flash(f'Staff member {staff.name} created successfully!', 'success')
            return redirect(url_for('crm.admin_staff'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating staff: {e}")
            flash('Error creating staff member. Please try again.', 'danger')

    return render_template('crm/staff_form.html', form=form, title='Add Staff Member')


@bp.route('/admin/staff/<int:staff_id>/edit', methods=['GET', 'POST'])
@crm_admin_required
def admin_edit_staff(staff_id):
    """Edit marketing staff - requires admin authentication"""
    staff = MarketingStaff.query.get_or_404(staff_id)
    form = StaffManagementForm(staff_id=staff_id, obj=staff)

    # Don't require password change on edit
    form.password.validators = [Optional()]
    form.confirm_password.validators = [Optional()]

    if form.validate_on_submit():
        staff.name = form.name.data
        staff.phone_number = form.phone_number.data
        staff.email = form.email.data
        staff.is_active = form.is_active.data

        # Only update password if provided
        if form.password.data:
            staff.set_password(form.password.data)

        try:
            db.session.commit()

            # Log activity
            log_audit('admin', current_user.id, 'updated', 'staff', staff.id,
                     f'Updated staff account: {staff.name}')

            flash(f'Staff member {staff.name} updated successfully!', 'success')
            return redirect(url_for('crm.admin_staff'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating staff: {e}")
            flash('Error updating staff member. Please try again.', 'danger')

    return render_template('crm/staff_form.html', form=form, staff=staff, title='Edit Staff Member')


@bp.route('/admin/staff/<int:staff_id>/delete', methods=['POST'])
@crm_admin_required
def admin_delete_staff(staff_id):
    """Delete marketing staff - requires admin authentication"""
    staff = MarketingStaff.query.get_or_404(staff_id)

    try:
        # Check if staff has assigned leads
        assigned_leads = Lead.query.filter_by(assigned_to=staff_id).count()
        if assigned_leads > 0:
            flash(f'Cannot delete staff member. They have {assigned_leads} assigned leads. Please reassign leads first.', 'danger')
            return redirect(url_for('crm.admin_staff'))

        # Log before deletion
        log_audit('admin', current_user.id, 'deleted', 'staff', staff_id,
                 f'Deleted staff account: {staff.name}')

        db.session.delete(staff)
        db.session.commit()

        flash(f'Staff member {staff.name} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting staff: {e}")
        flash('Error deleting staff member. Please try again.', 'danger')

    return redirect(url_for('crm.admin_staff'))


@bp.route('/admin/staff/<int:staff_id>/toggle-status', methods=['POST'])
@crm_admin_required
def admin_toggle_staff_status(staff_id):
    """Toggle staff active/inactive status - requires admin authentication"""
    staff = MarketingStaff.query.get_or_404(staff_id)

    staff.is_active = not staff.is_active
    status_text = 'activated' if staff.is_active else 'deactivated'

    try:
        db.session.commit()

        # Log activity
        log_audit('admin', current_user.id, 'updated', 'staff', staff.id,
                 f'Staff account {status_text}: {staff.name}')

        flash(f'Staff member {staff.name} {status_text} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating staff status: {e}")
        flash('Error updating staff status. Please try again.', 'danger')

    return redirect(url_for('crm.admin_staff'))


@bp.route('/admin/bulk-assign-leads', methods=['GET', 'POST'])
@crm_admin_required
def admin_bulk_assign_leads():
    """Bulk assign unassigned leads to staff members - requires admin authentication"""
    form = BulkAssignLeadsForm()
    
    # Get all active staff
    active_staff = MarketingStaff.query.filter_by(is_active=True).all()
    
    if form.validate_on_submit():
        assignments = {}
        total_assigned = 0
        
        # Collect assignments from form data
        for staff in active_staff:
            num_leads = request.form.get(f'staff_{staff.id}', 0, type=int)
            if num_leads > 0:
                assignments[staff.id] = num_leads
                total_assigned += num_leads
        
        if total_assigned == 0:
            flash('Please specify at least one lead to assign.', 'warning')
            return redirect(url_for('crm.admin_bulk_assign_leads'))
        
        # Get unassigned leads, ordered by creation date (oldest first)
        unassigned_leads = Lead.query.filter_by(assigned_to=None).order_by(Lead.created_at.asc()).limit(total_assigned).all()
        
        if len(unassigned_leads) < total_assigned:
            flash(f'Only {len(unassigned_leads)} unassigned leads available, but {total_assigned} requested.', 'danger')
            return redirect(url_for('crm.admin_bulk_assign_leads'))
        
        # Assign leads to staff
        lead_index = 0
        for staff_id, num in assignments.items():
            staff = MarketingStaff.query.get(staff_id)
            for i in range(num):
                lead = unassigned_leads[lead_index]
                lead.assigned_to = staff_id
                lead_index += 1
                
                # Log activity
                log_audit('admin', current_user.id, 'assigned', 'lead', lead.id, 
                         f'Assigned lead to {staff.name}')
                log_lead_activity(lead.id, staff_id, 'assigned', f'Lead assigned to {staff.name}')
        
        try:
            db.session.commit()
            flash(f'Successfully assigned {total_assigned} leads to staff members.', 'success')
            return redirect(url_for('crm.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error bulk assigning leads: {e}")
            flash('Error assigning leads. Please try again.', 'danger')
    
    # Get unassigned leads count for display
    unassigned_count = Lead.query.filter_by(assigned_to=None).count()
    
    return render_template('crm/bulk_assign_leads.html', 
                         form=form, 
                         active_staff=active_staff, 
                         unassigned_count=unassigned_count,
                         title='Bulk Assign Leads')


@bp.route('/admin/bulk-delete-leads', methods=['GET', 'POST'])
@crm_admin_required
def admin_bulk_delete_leads():
    """Bulk delete selected leads - requires admin authentication"""
    if request.method == 'POST':
        lead_ids = request.form.getlist('lead_ids[]')
        
        if not lead_ids:
            flash('No leads selected for deletion.', 'warning')
            return redirect(url_for('crm.admin_bulk_delete_leads'))
        
        try:
            # Convert string IDs to integers
            lead_ids = [int(lead_id) for lead_id in lead_ids]
            
            # Get leads to be deleted for logging
            leads_to_delete = Lead.query.filter(Lead.id.in_(lead_ids)).all()
            
            # Log deletions before deleting
            for lead in leads_to_delete:
                log_audit('admin', current_user.id, 'deleted', 'lead', lead.id, 
                         f'Bulk deleted lead: {lead.business_name}')
            
            # Delete the leads (cascade will handle related notes and activities)
            deleted_count = Lead.query.filter(Lead.id.in_(lead_ids)).delete(synchronize_session=False)
            
            db.session.commit()
            flash(f'Successfully deleted {deleted_count} leads.', 'success')
            return redirect(url_for('crm.admin_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error bulk deleting leads: {e}")
            flash('Error deleting leads. Please try again.', 'danger')
    
    # GET request - show leads selection page
    # Get all leads with pagination and search
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    
    query = Lead.query
    
    # Apply search
    if search_query:
        query = query.filter(
            or_(
                Lead.lead_name.ilike(f'%{search_query}%'),
                Lead.business_name.ilike(f'%{search_query}%'),
                Lead.phone_number.ilike(f'%{search_query}%'),
                Lead.email.ilike(f'%{search_query}%')
            )
        )
    
    # Apply status filter
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Lead.created_at))
    
    # Pagination
    leads = query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('crm/bulk_delete_leads.html',
                         leads=leads,
                         search_query=search_query,
                         status_filter=status_filter,
                         title='Bulk Delete Leads')


@bp.route('/admin/delete-all-leads', methods=['POST'])
@crm_admin_required
def admin_delete_all_leads():
    """Delete all leads - requires admin authentication and confirmation"""
    try:
        # Get count before deletion for logging
        total_count = Lead.query.count()
        
        if total_count == 0:
            flash('No leads to delete.', 'info')
            return redirect(url_for('crm.admin_dashboard'))
        
        # Log the deletion action before deleting
        log_audit('admin', current_user.id, 'deleted_all', 'lead', 
                 description=f'Deleted all {total_count} leads from the system')
        
        # Delete all leads (cascade will handle related notes and activities)
        deleted_count = Lead.query.delete(synchronize_session=False)
        
        db.session.commit()
        flash(f'Successfully deleted all {deleted_count} leads from the system.', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting all leads: {e}")
        flash('Error deleting all leads. Please try again.', 'danger')
    
    return redirect(url_for('crm.admin_dashboard'))


# ============= Marketing Staff Routes =============

@bp.route('/staff/logout')
def staff_logout():
    """Marketing staff logout"""
    if 'staff_id' in session:
        staff_id = session['staff_id']
        log_audit('staff', staff_id, 'logout', 'session', description='Staff logged out')
        session.pop('staff_id', None)
        session.pop('staff_name', None)
        flash('You have been logged out.', 'info')
    return redirect(url_for('auth.staff_login'))


@bp.route('/staff/dashboard')
@staff_login_required
def staff_dashboard():
    """Marketing staff dashboard"""
    staff_id = session.get('staff_id')
    staff = MarketingStaff.query.get_or_404(staff_id)
    
    # Search and filter
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    sort_by = request.args.get('sort_by', 'created_at_desc')
    
    # Base query - staff can see all leads or only assigned leads
    # For now, showing all leads (can be restricted later)
    query = Lead.query
    
    # Apply search
    if search_query:
        query = query.filter(
            or_(
                Lead.lead_name.ilike(f'%{search_query}%'),
                Lead.business_name.ilike(f'%{search_query}%'),
                Lead.phone_number.ilike(f'%{search_query}%')
            )
        )
    
    # Apply status filter
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # Apply sorting
    if sort_by == 'created_at_asc':
        query = query.order_by(asc(Lead.created_at))
    elif sort_by == 'business_name_asc':
        query = query.order_by(asc(Lead.business_name))
    elif sort_by == 'business_name_desc':
        query = query.order_by(desc(Lead.business_name))
    elif sort_by == 'status':
        query = query.order_by(Lead.status)
    else:  # created_at_desc
        query = query.order_by(desc(Lead.created_at))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    leads = query.paginate(page=page, per_page=20, error_out=False)
    
    # Statistics
    my_leads = Lead.query.filter_by(assigned_to=staff_id).count()
    total_leads = Lead.query.count()
    
    return render_template('crm/staff_dashboard.html',
                         title='Lead Management Dashboard',
                         staff=staff,
                         leads=leads,
                         my_leads=my_leads,
                         total_leads=total_leads,
                         search_query=search_query,
                         status_filter=status_filter,
                         sort_by=sort_by)


@bp.route('/staff/lead/<int:lead_id>')
@staff_login_required
def staff_view_lead(lead_id):
    """View lead details"""
    staff_id = session.get('staff_id')
    staff = MarketingStaff.query.get_or_404(staff_id)
    lead = Lead.query.get_or_404(lead_id)
    
    # Log view activity
    log_lead_activity(lead_id, staff_id, 'viewed', f'Lead viewed by {staff.name}')
    
    # Get notes and activities
    notes = LeadNote.query.filter_by(lead_id=lead_id).order_by(desc(LeadNote.created_at)).all()
    activities = LeadActivity.query.filter_by(lead_id=lead_id).order_by(desc(LeadActivity.created_at)).limit(20).all()
    
    # Generate message for WhatsApp/SMS
    lead_display_name = lead.lead_name if lead.lead_name else lead.business_name
    message = f"Hello {lead_display_name},\n\n"
    message += f"My name is {staff.name} from Kodeminds Software Solution.\n\n"
    message += f"We provide all kinds of software-related services including website and business management software for {lead.business_name}.\n\n"
    message += "Please contact us at +918458804893 or visit our website https://kodeminds.com"
    
    encoded_message = quote(message)
    
    return render_template('crm/lead_view.html',
                         title=f'Lead: {lead.business_name}',
                         lead=lead,
                         staff=staff,
                         notes=notes,
                         activities=activities,
                         encoded_message=encoded_message)


@bp.route('/staff/lead/<int:lead_id>/add-note', methods=['POST'])
@staff_login_required
def staff_add_note(lead_id):
    """Add note to lead"""
    staff_id = session.get('staff_id')
    lead = Lead.query.get_or_404(lead_id)
    
    note_text = request.form.get('note')
    if note_text:
        note = LeadNote(
            lead_id=lead_id,
            staff_id=staff_id,
            note=note_text
        )
        
        try:
            db.session.add(note)
            db.session.commit()
            
            # Log activity
            log_lead_activity(lead_id, staff_id, 'note_added', f'Note added: {note_text[:50]}...')
            
            flash('Note added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding note: {e}")
            flash('Error adding note.', 'danger')
    
    return redirect(url_for('crm.staff_view_lead', lead_id=lead_id))


@bp.route('/staff/lead/<int:lead_id>/update-status', methods=['POST'])
@staff_login_required
def staff_update_status(lead_id):
    """Update lead status"""
    staff_id = session.get('staff_id')
    lead = Lead.query.get_or_404(lead_id)
    
    new_status = request.form.get('status')
    if new_status in ['new', 'contacted', 'in_progress', 'won', 'lost']:
        old_status = lead.status
        lead.status = new_status
        lead.updated_at = datetime.utcnow()
        
        if new_status == 'contacted':
            lead.last_contacted = datetime.utcnow()
        
        try:
            db.session.commit()
            
            # Log activity
            log_lead_activity(lead_id, staff_id, 'status_change', 
                            f'Status changed from {old_status} to {new_status}')
            
            flash(f'Lead status updated to {new_status}!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating status: {e}")
            flash('Error updating status.', 'danger')
    
    return redirect(url_for('crm.staff_view_lead', lead_id=lead_id))


@bp.route('/staff/lead/<int:lead_id>/log-activity', methods=['POST'])
@staff_login_required
def staff_log_activity(lead_id):
    """Log activity (call, whatsapp, sms)"""
    staff_id = session.get('staff_id')
    lead = Lead.query.get_or_404(lead_id)
    
    activity_type = request.form.get('activity_type')
    if activity_type in ['call', 'whatsapp', 'sms', 'email']:
        log_lead_activity(lead_id, staff_id, activity_type, 
                         f'{activity_type.capitalize()} initiated')
        
        # Update last contacted
        lead.last_contacted = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'{activity_type.capitalize()} logged'})
    
    return jsonify({'success': False, 'message': 'Invalid activity type'}), 400


@bp.route('/staff/lead/<int:lead_id>/delete', methods=['POST'])
@staff_login_required
def staff_delete_lead(lead_id):
    """Delete lead"""
    staff_id = session.get('staff_id')
    lead = Lead.query.get_or_404(lead_id)
    
    try:
        # Log before deletion
        log_audit('staff', staff_id, 'deleted', 'lead', lead_id, 
                 f'Deleted lead: {lead.business_name}')
        
        db.session.delete(lead)
        db.session.commit()
        
        flash('Lead deleted successfully!', 'success')
        return jsonify({'success': True, 'redirect': url_for('crm.staff_dashboard')})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting lead: {e}")
        return jsonify({'success': False, 'message': 'Error deleting lead'}), 500


@bp.route('/staff/lead/<int:lead_id>/edit', methods=['GET', 'POST'])
@staff_login_required
def staff_edit_lead(lead_id):
    """Edit lead"""
    staff_id = session.get('staff_id')
    staff = MarketingStaff.query.get_or_404(staff_id)
    lead = Lead.query.get_or_404(lead_id)
    
    form = EditLeadForm(obj=lead)
    
    # Populate staff choices
    staff_list = MarketingStaff.query.filter_by(is_active=True).all()
    form.assigned_to.choices = [(0, 'Unassigned')] + [(s.id, s.name) for s in staff_list]
    
    if form.validate_on_submit():
        lead.lead_name = form.lead_name.data
        lead.business_name = form.business_name.data
        lead.phone_number = form.phone_number.data
        lead.email = form.email.data
        lead.business_address = form.business_address.data
        lead.status = form.status.data
        lead.priority = form.priority.data
        lead.source = form.source.data
        lead.assigned_to = form.assigned_to.data if form.assigned_to.data != 0 else None
        lead.follow_up_date = form.follow_up_date.data
        lead.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            log_lead_activity(lead_id, staff_id, 'updated', 'Lead information updated')
            flash('Lead updated successfully!', 'success')
            return redirect(url_for('crm.staff_view_lead', lead_id=lead_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating lead: {e}")
            flash('Error updating lead.', 'danger')
    
    return render_template('crm/edit_lead.html', form=form, lead=lead, staff=staff, title='Edit Lead')


# ============= Bulk Operations =============

@bp.route('/admin/leads/export')
@crm_admin_required
def admin_export_leads():
    """Export leads to CSV - requires admin authentication"""
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Lead Name', 'Business Name', 'Phone', 'Email', 
                    'Address', 'Status', 'Priority', 'Source', 'Assigned To', 
                    'Created At', 'Follow-up Date'])
    
    # Write data
    leads = Lead.query.all()
    for lead in leads:
        assigned_name = lead.assigned_staff.name if lead.assigned_staff else 'Unassigned'
        writer.writerow([
            lead.id,
            lead.lead_name or '',
            lead.business_name,
            lead.phone_number,
            lead.email or '',
            lead.business_address,
            lead.status,
            lead.priority,
            lead.source or '',
            assigned_name,
            lead.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            lead.follow_up_date.strftime('%Y-%m-%d %H:%M:%S') if lead.follow_up_date else ''
        ])
    
    # Prepare response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'leads_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    )


@bp.route('/admin/leads/import', methods=['POST'])
@crm_admin_required
def admin_import_leads():
    """Import leads from CSV - requires admin authentication"""
    if 'file' not in request.files:
        flash('No file uploaded.', 'danger')
        return redirect(url_for('crm.admin_dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('crm.admin_dashboard'))
    
    if file and file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            imported_count = 0
            for row in csv_reader:
                lead = Lead(
                    lead_name=row.get('Lead Name'),
                    business_name=row.get('Business Name'),
                    phone_number=row.get('Phone'),
                    email=row.get('Email'),
                    business_address=row.get('Address'),
                    status=row.get('Status', 'new'),
                    priority=row.get('Priority', 'medium'),
                    source=row.get('Source'),
                    created_by_admin=current_user.id
                )
                db.session.add(lead)
                imported_count += 1
            
            db.session.commit()
            flash(f'Successfully imported {imported_count} leads!', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error importing leads: {e}")
            flash('Error importing leads. Please check the file format.', 'danger')
    else:
        flash('Please upload a CSV file.', 'danger')
    
    return redirect(url_for('crm.admin_dashboard'))


# ============= Message Templates =============

@bp.route('/admin/templates')
@crm_admin_required
def admin_templates():
    """Manage message templates - requires admin authentication"""
    templates = MessageTemplate.query.all()
    return render_template('crm/templates.html', templates=templates, title='Message Templates')


@bp.route('/admin/templates/add', methods=['GET', 'POST'])
@crm_admin_required
def admin_add_template():
    """Add message template - requires admin authentication"""
    form = MessageTemplateForm()
    
    if form.validate_on_submit():
        template = MessageTemplate(
            name=form.name.data,
            template_type=form.template_type.data,
            subject=form.subject.data,
            content=form.content.data,
            is_active=form.is_active.data
        )
        
        try:
            db.session.add(template)
            db.session.commit()
            
            # Log activity
            log_audit('admin', current_user.id, 'created', 'template', template.id, 
                     f'Created template: {template.name}')
            
            flash('Template created successfully!', 'success')
            return redirect(url_for('crm.admin_templates'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating template: {e}")
            flash('Error creating template.', 'danger')
    
    return render_template('crm/template_form.html', form=form, title='Add Template')


@bp.route('/admin/templates/<int:template_id>/edit', methods=['GET', 'POST'])
@crm_admin_required
def admin_edit_template(template_id):
    """Edit message template - requires admin authentication"""
    template = MessageTemplate.query.get_or_404(template_id)
    form = MessageTemplateForm(obj=template)
    
    if form.validate_on_submit():
        template.name = form.name.data
        template.template_type = form.template_type.data
        template.subject = form.subject.data
        template.content = form.content.data
        template.is_active = form.is_active.data
        
        try:
            db.session.commit()
            
            # Log activity
            log_audit('admin', current_user.id, 'updated', 'template', template.id, 
                     f'Updated template: {template.name}')
            
            flash('Template updated successfully!', 'success')
            return redirect(url_for('crm.admin_templates'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating template: {e}")
            flash('Error updating template.', 'danger')
    
    return render_template('crm/template_form.html', form=form, template=template, title='Edit Template')


@bp.route('/admin/templates/<int:template_id>/delete', methods=['POST'])
@crm_admin_required
def admin_delete_template(template_id):
    """Delete message template - requires admin authentication"""
    template = MessageTemplate.query.get_or_404(template_id)
    
    try:
        # Log before deletion
        log_audit('admin', current_user.id, 'deleted', 'template', template_id, 
                 f'Deleted template: {template.name}')
        
        db.session.delete(template)
        db.session.commit()
        
        flash('Template deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting template: {e}")
        flash('Error deleting template.', 'danger')
    
    return redirect(url_for('crm.admin_templates'))


@bp.route('/admin/templates/<int:template_id>/toggle-status', methods=['POST'])
@crm_admin_required
def admin_toggle_template_status(template_id):
    """Toggle template active/inactive status - requires admin authentication"""
    template = MessageTemplate.query.get_or_404(template_id)
    
    template.is_active = not template.is_active
    status_text = 'activated' if template.is_active else 'deactivated'
    
    try:
        db.session.commit()
        
        # Log activity
        log_audit('admin', current_user.id, 'updated', 'template', template.id, 
                 f'Template {status_text}: {template.name}')
        
        flash(f'Template {status_text} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating template status: {e}")
        flash('Error updating template status.', 'danger')
    
    return redirect(url_for('crm.admin_templates'))


# ============= Audit Logs =============

@bp.route('/admin/audit-logs')
@crm_admin_required
def admin_audit_logs():
    """View audit logs - requires admin authentication"""
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(desc(AuditLog.created_at)).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('crm/audit_logs.html', logs=logs, title='Audit Logs')
