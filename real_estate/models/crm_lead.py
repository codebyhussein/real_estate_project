from odoo import models, fields


class LeadForm(models.Model):
    _name = 'lead.form'
    _description = 'Lead Form Submission'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    phone = fields.Char(string='Phone')

    company = fields.Char(string='Company')
    job_position = fields.Char(string='Job Position')

    budget = fields.Float(string='Budget')
    interested_service = fields.Char(string='Interested Service')

    message = fields.Text(string='Message')

    score = fields.Float(string='Lead Score')
    source = fields.Char(string='Source')