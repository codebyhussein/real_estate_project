
from odoo import models, fields


class TenantWizard(models.TransientModel):
    _name = 'real_estate.tenant.wizard'
    _description = 'Tenant Wizard'

    name = fields.Char(
        string='Tenant Name',
        required=True
    )

    email = fields.Char(
        string='Email',
        required=True
    )

    phone = fields.Char(
        string='Phone Number'
    )

    mobile = fields.Char(
        string='Mobile Number'
    )

    city = fields.Char(
        string='City'
    )

    date_of_birth = fields.Date(
        string='Date of Birth'
    )

    notes = fields.Text(
        string='Notes'
    )

    user_id = fields.Many2one(
        'res.users',
        string='Related User'
    )

    led_id = fields.Many2one(
        'crm.lead',
        string='CRM Lead',
        readonly=True
    )

    age_categroy = fields.Selection([
        ('A', '20 - 40'),
        ('B', '41 - 60'),
        ('C', '61 - 80'),
        ('D', '81 - 100')
    ], string='Age Category')

    def create_tenant(self):
        self.ensure_one()
        tenant =  self.env['real_estate.tenant'].sudo().create({
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'city': self.city,
            'date_of_birth': self.date_of_birth,
            'notes': self.notes,
            'user_id': self.user_id.id,
            'led_id': self.led_id.id,
            'age_categroy': self.age_categroy,
        })

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': 'Tenant Created',
        #         'message': 'Tenant has been created successfully.',
        #         'type': 'success',
        #         'sticky': False,
        #         'next': {
        #             'type': 'ir.actions.act_window_close',
        #         },
        #     },
        # }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'real_estate.tenant',
            'res_id': tenant.id,
            'views': [(False, 'form')],
            'target': 'current',
        }
