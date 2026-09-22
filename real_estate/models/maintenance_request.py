
from datetime import timedelta

from odoo import api, fields, models


class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _description = 'Property Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Maintenance Reference',
        required=True,
        tracking=True,
        copy=False,
        default='New',
    )

    lease_id = fields.Many2one(
        'real_estate.lease',
        string='Lease',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )

    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        related='lease_id.tenant_id',
        store=True,
        readonly=True,
    )

    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        related='lease_id.property_id',
        store=True,
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
        tracking=True,
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
        tracking=True,
    )

    assigned_to = fields.Many2one(
        'res.users',
        string='Assigned To',
        tracking=True,
    )

    preferred_date = fields.Date(
        string='Preferred Date',
    )

    scheduled_date = fields.Date(
        string='Scheduled Date',
    )

    completion_date = fields.Date(
        string='Completion Date',
        readonly=True,
    )

    actual_cost = fields.Float(
        string='Actual Cost',
        tracking=True,
    )

    tenant_phone = fields.Char(
        string='Tenant Phone',
        related='tenant_id.phone',
        store=True,
        readonly=True,
    )

    state = fields.Selection(
        [
            ('submitted', 'Submitted'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='submitted',
        required=True,
        tracking=True,
    )

    # ==========================================================
    # CREATE
    # ==========================================================

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('name') == 'New':
            vals['name'] = (
                self.env['ir.sequence'].next_by_code(
                    'real_estate.maintenance'
                )
                or 'New'
            )

        return super().create(vals)

    # ==========================================================
    # STATE ACTIONS
    # ==========================================================

    def action_start(self):
        for record in self:
            record.write({
                'state': 'in_progress',
            })

    def action_complete(self):
        for record in self:
            record.write({
                'state': 'completed',
                'completion_date': fields.Date.today(),
            })

    def action_cancel(self):
        for record in self:
            record.write({
                'state': 'cancelled',
            })

    def action_reset(self):
        for record in self:
            record.write({
                'state': 'submitted',
                'completion_date': False,
            })
            
            
    api.model
    def _cron_auto_complete_maintenance_requests(self):
        """Scheduled action - complete maintenance requests that are in progress and have a scheduled date in the past"""
        today = fields.Date.today()
        maintenance_requests_urgency = self.search([
            ('urgency', '=', 'emergency'),
           
        ])
        for request in maintenance_requests_urgency:
            request.write({
                 
                'scheduled_date': today+timedelta(days=1),
            })