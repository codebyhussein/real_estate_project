

from odoo import api, fields, models


class LeaseInherit(models.Model):
    _inherit = 'real_estate.lease'

    maintenance_count = fields.Integer(
        string='Maintenance Requests',
        compute='_compute_maintenance_count',
        store=True
    )
    
    total_viza_amount = fields.Float(string='Total Amount with Viza', compute='_compute_payment_method_amounts', store=True)
    total_cash_amount = fields.Float(string='Total Amount with Cash', compute='_compute_payment_method_amounts', store=True)
    total_credit_card_amount = fields.Float(string='Total Amount with Credit Card', compute='_compute_payment_method_amounts', store=True)
    total_check_amount = fields.Float(string='Total Amount with Check', compute='_compute_payment_method_amounts', store=True)
    total_other_amount = fields.Float(string='Total Amount with Other', compute='_compute_payment_method_amounts', store=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    payment_ids = fields.One2many('lease.payment',
    'lease_id',
    string='Payments',
)
    @api.depends('maintenance_request_ids')
    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = len(
                record.maintenance_request_ids
            )

    def action_view_maintenance(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Requests',
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form',
            'domain': [
                ('lease_id', '=', self.id)
            ],
            'context': {
                'default_lease_id': self.id,
                'default_tenant_id': self.tenant_id.id,
                'default_property_id': self.property_id.id,
            },
        }

    def action_create_maintenance(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Maintenance Request',
            'res_model': 'maintenance.request.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lease_id': self.id,
                'default_tenant_id': self.tenant_id.id,
                'default_property_id': self.property_id.id,
                'default_tenant_phone': (
                    self.tenant_id.mobile or self.tenant_id.phone
                ),
                'default_assigned_to': self.user_id.id,
            },
        }
    
    
    
    @api.depends('payment_ids.amount', 'payment_ids.payment_method')
    def _compute_payment_method_amounts(self):
        for record in self:
            amounts = {
                method_name: sum(
                    record.payment_ids.filtered(
                        lambda payment: payment.payment_method == method_name
                    ).mapped('amount')
                )
                for method_name in ['viza', 'cash', 'credit_card', 'check', 'other']
            }

            record.total_viza_amount = amounts['viza']
            record.total_cash_amount = amounts['cash']
            record.total_credit_card_amount = amounts['credit_card']
            record.total_check_amount = amounts['check']
            record.total_other_amount = amounts['other']


    @api.depends('payment_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.payment_ids.mapped('amount'))