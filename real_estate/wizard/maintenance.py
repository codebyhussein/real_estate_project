# from odoo import models, fields, api

# class MaintenanceRequestWizard(models.TransientModel):
#     _name = 'maintenance.request.wizard'
#     _description = 'Maintenance Request Wizard'
    
#     lease_id = fields.Many2one('real_estate.lease', required=True)
#     property_id = fields.Many2one('real_estate.property', related='lease_id.property_id', readonly=True)
    
#     issue_type = fields.Selection([
#         ('plumbing', 'Plumbing'),
#         ('electrical', 'Electrical'),
#         ('air_condition', 'Air Condition'),
#         ('appliance', 'Appliance'),
#         ('other', 'Other')
#     ], required=True)
    
#     description = fields.Text(required=True)
#     urgency = fields.Selection([
#         ('low', 'Low'),
#         ('medium', 'Medium'),
#         ('high', 'High'),
#         ('emergency', 'Emergency')
#     ], default='medium', required=True)
    
#     preferred_date = fields.Date()
#     tenant_phone = fields.Char()
    
#     def action_submit_request(self):
#         """Create maintenance request and notify manager"""
#         self.ensure_one()
        
#         # 1. Create maintenance.request record
#         maintenance_request = self.env['maintenance.request'].create({
#             'property_id': self.property_id.id,
#             'lease_id': self.lease_id.id,
#             'issue_type': self.issue_type,
#             'description': self.description,
#             'urgency': self.urgency,
#             'scheduled_date': self.preferred_date,
#             'tenant_phone': self.tenant_phone,
#             'state': 'submitted',
#         })
        
#         # 2. Send notification to property manager (Agent)
#         # if self.property_id.agent_id:
#         #     maintenance_request.activity_schedule(
#         #         'mail.mail_activity_data_todo',
#         #         user_id=self.property_id.agent_id.id,
#         #         summary=f"New {self.issue_type.capitalize()} Maintenance Request",
#         #         note=f"Urgency: {self.urgency}\nDescription: {self.description}"
#         #     )
        
#         # # 3. Return action to close wizard and show confirmation
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'display_notification',
#             'params': {
#                 'title': 'Request Submitted',
#                 'message': 'Your maintenance request has been submitted successfully and the manager has been notified.',
#                 'type': 'success',
#                 'sticky': False,
#                 'next': {'type': 'ir.actions.act_window_close'},
#             },}
        
            
#         # }
#         #         # 4. Opening a Created Record
#         # return {
#         #     'type': 'ir.actions.act_window',
#         #     'res_model': 'maintenance.request',
#         #     'res_id': maintenance_request.id,
#         #     'views': [(False, 'form')],
#         #     'target': 'current',
#         # }
from odoo import fields, models


class MaintenanceRequestWizard(models.TransientModel):
    _name = 'maintenance.request.wizard'
    _description = 'Maintenance Request Wizard'

    lease_id = fields.Many2one(
        'real_estate.lease',
        string='Lease',
        required=True,
        readonly=True,
    )

    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        related='lease_id.property_id',
        readonly=True,
    )

    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        related='lease_id.tenant_id',
        readonly=True,
    )

    issue_type = fields.Selection(
        [
            ('plumbing', 'Plumbing'),
            ('electrical', 'Electrical'),
            ('air_condition', 'Air Condition'),
            ('appliance', 'Appliance'),
            ('other', 'Other'),
        ],
        string='Issue Type',
        required=True,
    )

    description = fields.Text(
        string='Description',
        required=True,
    )

    urgency = fields.Selection(
        [
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('emergency', 'Emergency'),
        ],
        string='Urgency',
        default='medium',
        required=True,
    )

    preferred_date = fields.Date(
        string='Preferred Date',
    )

    tenant_phone = fields.Char(
        string='Tenant Phone',
        related='lease_id.tenant_id.phone',
        readonly=True,
    )

    def action_submit_request(self):
        self.ensure_one()

        self.env['maintenance.request'].create({
            'lease_id': self.lease_id.id,
            'issue_type': self.issue_type,
            'description': self.description,
            'urgency': self.urgency,
            'scheduled_date': self.preferred_date,
            'tenant_phone': self.tenant_phone,
            'state': 'submitted',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Request Submitted',
                'message': (
                    'Maintenance request has been submitted successfully.'
                ),
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                },
            },
        }