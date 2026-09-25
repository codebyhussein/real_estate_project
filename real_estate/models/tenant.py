from passlib import context

from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from odoo import models, fields, api

class Tenant(models.Model):
    _name = 'real_estate.tenant'
    _description = 'Real Estate Tenant'
    _order = 'name asc'
    
    # === CORE FIELDS ===
    name = fields.Char(string='Tenant Name', required=True, index=True)
    email = fields.Char(string='Email', required=True, index=True)
    phone = fields.Char(string='Phone Number')
    mobile = fields.Char(string='Mobile Number')
    city = fields.Char(string='City')
    date_joined = fields.Date(string='Date Joined', default=fields.Date.today, readonly=True)
    date_of_birth = fields.Date(string='Date of Birth')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(string='Active', default=True)
    user_id = fields.Many2one('res.users', string='Related User', index=True)
    lease_ids =fields.One2many('real_estate.lease','tenant_id' ,string='Leases')
    property_type= fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('commercial', 'Commercial'),
        ('land', 'Land'),       ], string='Property Type',required=True) 

  
    led_id= fields.Many2one('crm.lead', string='CRM Lead',)
    age_categroy = fields.Selection([
        ('A', '20 - 40'),
        ('B', '41 - 60'),
        ('C', '61 - 80'),
        ('D', '81 - 100')
    ], string='Age Category',)


    def update_notes(self,):
        """Update the notes field with a new note"""
        for record in self:
            record.write({'notes': record.name})

    
    def get_lead_name(self,):
        """Update the notes field with a new note"""
        for record in self:
            record.write({'notes': record.led_id.name})






    def get_lead_website(self):
        for record in self:
            if record.led_id.website: # type: ignore
                record.write({'notes': record.led_id.website})
            else:
                record.write({'notes': record.led_id.email_from})
                
                    

    @api.model
    def _cron_create_tenant(self):
        leads = self.env['crm.lead'].search([
            ('property_type', '!=', False),
        ], limit=1)

        for lead in leads:
            self.create({
                'name': lead.name,
                'email': lead.email_from,
                'phone': lead.phone,
                'mobile': lead.mobile,
                'city': lead.city,
                'led_id': lead.id,
            })
            
            
 

    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for record in self:
            if record.date_of_birth < fields.Date.today():
                raise ValidationError(
                    'Date of birth cannot be in the future.'
                )
                
    # added sql constrains for email address
    
    _sql_constraints = [('unique_email', 'UNIQUE(email)', 'Email must be unique! This email is already registered.'),]
    
    
    
    # create a portal user using button in tenant view 
    
    def action_create_portal_user(self):
        for record in self:
            if record.user_id:
                raise UserError(
                    "This tenant already has a related user."
                )

            if not record.email:
                raise UserError(
                    "Please add an email before creating the portal user."
                )

            # Check if a user already exists with this email
            existing_user = self.env['res.users'].sudo().search(
                [('login', '=', record.email)],
                limit=1
            )

            if existing_user:
                raise UserError(
                    "A user already exists with this email."
                )

            portal_group = self.env.ref('base.group_portal')

            user = self.env['res.users'].sudo().create({
                'name': record.name,
                'login': record.email,
                'email': record.email,
                'groups_id': [(6, 0, [portal_group.id])],
            })

            record.user_id = user.id


  


