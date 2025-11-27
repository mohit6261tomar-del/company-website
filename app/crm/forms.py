from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateTimeField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError, EqualTo
from app.models import MarketingStaff, Lead


class BulkAssignLeadsForm(FlaskForm):
    """Form for bulk assigning leads to staff"""
    submit = SubmitField('Assign Leads')


class CRMAdminLoginForm(FlaskForm):
    """Admin login form for CRM"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class MarketingStaffLoginForm(FlaskForm):
    """Marketing staff login form"""
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class MarketingStaffRegistrationForm(FlaskForm):
    """Marketing staff registration form"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_phone_number(self, phone_number):
        staff = MarketingStaff.query.filter_by(phone_number=phone_number.data).first()
        if staff:
            raise ValidationError('This phone number is already registered.')


class AddLeadForm(FlaskForm):
    """Form for adding a new lead"""
    lead_name = StringField('Lead Name', validators=[Optional(), Length(max=100)])
    business_name = StringField('Business Name', validators=[DataRequired(), Length(min=2, max=200)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    business_address = TextAreaField('Business Address', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('in_progress', 'In Progress'),
        ('won', 'Won'),
        ('lost', 'Lost')
    ], default='new')
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium')
    source = StringField('Source', validators=[Optional(), Length(max=50)])
    assigned_to = SelectField('Assign To', coerce=int, validators=[Optional()])
    follow_up_date = DateTimeField('Follow-up Date', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField('Add Lead')


class EditLeadForm(FlaskForm):
    """Form for editing a lead"""
    lead_name = StringField('Lead Name', validators=[Optional(), Length(max=100)])
    business_name = StringField('Business Name', validators=[DataRequired(), Length(min=2, max=200)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    business_address = TextAreaField('Business Address', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('in_progress', 'In Progress'),
        ('won', 'Won'),
        ('lost', 'Lost')
    ])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ])
    source = StringField('Source', validators=[Optional(), Length(max=50)])
    assigned_to = SelectField('Assign To', coerce=int, validators=[Optional()])
    follow_up_date = DateTimeField('Follow-up Date', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    submit = SubmitField('Update Lead')


class LeadNoteForm(FlaskForm):
    """Form for adding notes to a lead"""
    note = TextAreaField('Note', validators=[DataRequired(), Length(min=1, max=5000)])
    submit = SubmitField('Add Note')


class MessageTemplateForm(FlaskForm):
    """Form for creating message templates"""
    name = StringField('Template Name', validators=[DataRequired(), Length(min=2, max=100)])
    template_type = SelectField('Type', choices=[
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email')
    ], validators=[DataRequired()])
    subject = StringField('Subject (for Email)', validators=[Optional(), Length(max=200)])
    content = TextAreaField('Message Content', validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Template')


class SearchLeadForm(FlaskForm):
    """Form for searching leads"""
    search_query = StringField('Search', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('', 'All Status'),
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('in_progress', 'In Progress'),
        ('won', 'Won'),
        ('lost', 'Lost')
    ], validators=[Optional()])
    assigned_to = SelectField('Assigned To', coerce=int, validators=[Optional()])
    sort_by = SelectField('Sort By', choices=[
        ('created_at_desc', 'Newest First'),
        ('created_at_asc', 'Oldest First'),
        ('business_name_asc', 'Business Name A-Z'),
        ('business_name_desc', 'Business Name Z-A'),
        ('status', 'Status')
    ], default='created_at_desc')


class StaffManagementForm(FlaskForm):
    """Form for creating/editing marketing staff"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    password = PasswordField('Password', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[Optional(), EqualTo('password')])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Staff')

    def __init__(self, staff_id=None, *args, **kwargs):
        super(StaffManagementForm, self).__init__(*args, **kwargs)
        self.staff_id = staff_id

    def validate_phone_number(self, phone_number):
        if not self.staff_id:  # For new staff
            staff = MarketingStaff.query.filter_by(phone_number=phone_number.data).first()
            if staff:
                raise ValidationError('This phone number is already registered.')
        else:  # For editing existing staff
            staff = MarketingStaff.query.filter_by(phone_number=phone_number.data).first()
            if staff and staff.id != self.staff_id:
                raise ValidationError('This phone number is already registered.')
