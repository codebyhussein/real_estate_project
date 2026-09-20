from passlib import context

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
  


