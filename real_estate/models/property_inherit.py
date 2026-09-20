from odoo import models, fields, api


class PropertyInherit(models.Model):
    _inherit = 'real_estate.property'

    lease_count = fields.Integer(
        string='Leases',
        compute='_compute_lease_count'
    )

    @api.depends('lease_ids')
    def _compute_lease_count(self):
        for record in self:
            record.lease_count = len(record.lease_ids)

    def action_view_leases(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Leases',
            'res_model': 'real_estate.lease',
            'view_mode': 'tree,form',
            'domain': [
                ('property_id', '=', self.id)
            ],
            'context': {
                'default_property_id': self.id,
            },
        }