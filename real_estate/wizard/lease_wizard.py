
from odoo import models, fields


class LeaseWizard(models.TransientModel):
    _name = 'real_estate.lease.wizard'
    _description = 'Property Lease Wizard Agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Lease Reference',
        required=True,
        tracking=True
    )

    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        required=True,
        ondelete='cascade',
        index=True,
        readonly=True
    )

    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        required=True,
        ondelete='cascade',
        index=True
    )

    start_date = fields.Date(
        string='Start Date',
        required=True
    )

    end_date = fields.Date(
        string='End Date',
        required=True
    )

    monthly_rent = fields.Float(
        string='Monthly Rent',
        required=True
    )

    deposit_paid = fields.Float(
        string='Deposit Paid'
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True)

    user_id = fields.Many2one(
        'res.users',
        string='User Id'
    )

    def action_create_lease(self):
        self.ensure_one()

        lease = self.env['real_estate.lease'].create({
            'name': self.name,
            'property_id': self.property_id.id,
            'tenant_id': self.tenant_id.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'monthly_rent': self.monthly_rent,
            'deposit_paid': self.deposit_paid,
            'state': self.state,
            'user_id': self.user_id.id,
        })

        return {
              'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Success',
            'message': 'Lease created successfully.',
            'type': 'success',
            'sticky': False,
             'next': {'type': 'ir.actions.act_window_close'},
        }
        }
