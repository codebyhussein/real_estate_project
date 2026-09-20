from odoo import models, fields, api


class LeaseInherit(models.Model):
    _inherit = 'real_estate.lease'

    maintenance_count = fields.Integer(
        string='Maintenance Request',
        compute='_compute_maintenance_count'
    )

    @api.depends('maintenance_request_ids')
    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = len(record.maintenance_request_ids)

    def action_view_maintenance(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Request',
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form',
            'domain': [
                ('lease_id', '=', self.id)
            ],
            'context': {
                'default_lease_id': self.id,
            },
        }