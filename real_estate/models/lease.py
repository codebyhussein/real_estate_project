
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class Lease(models.Model):
    _name = 'real_estate.lease'
    _description = 'Property Lease Agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # =========================================================
    # Core Fields
    # =========================================================

    name = fields.Char(
        string='Lease Reference',
        required=True,
        tracking=True,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'real_estate.lease'
        ) or 'New',
    )

    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        required=True,
        ondelete='cascade',
        index=True,
    )

    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        required=True,
        ondelete='cascade',
        index=True,
    )

    start_date = fields.Date(
        string='Start Date',
        required=True,
    )

    end_date = fields.Date(
        string='End Date',
        required=True,
    )

    monthly_rent = fields.Float(
        string='Monthly Rent',
        required=True,
    )

    deposit_paid = fields.Float(
        string='Deposit Paid',
    )

    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        index=True,
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('at_risk', 'At Risk'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )

    # =========================================================
    # Maintenance
    # =========================================================

    maintenance_request_ids = fields.One2many(
        'maintenance.request',
        'lease_id',
        string='Maintenance Requests',
    )

    maintenance_count = fields.Integer(
        string='Maintenance Requests',
        compute='_compute_maintenance_count',
        store=True,
    )

    plumbing_cost = fields.Float(
        string='Plumbing Cost',
        compute='_compute_maintenance_costs',
        store=True,
    )

    electrical_cost = fields.Float(
        string='Electrical Cost',
        compute='_compute_maintenance_costs',
        store=True,
    )

    air_condition_cost = fields.Float(
        string='Air Condition Cost',
        compute='_compute_maintenance_costs',
        store=True,
    )

    appliance_cost = fields.Float(
        string='Appliance Cost',
        compute='_compute_maintenance_costs',
        store=True,
    )

    other_cost = fields.Float(
        string='Other Cost',
        compute='_compute_maintenance_costs',
        store=True,
    )

    total_cost = fields.Float(
        string='Total Maintenance Cost',
        compute='_compute_maintenance_costs',
        store=True,
    )

    # =========================================================
    # Lease Calculations
    # =========================================================

    duration_months = fields.Integer(
        string='Duration (Months)',
        compute='_compute_duration_months',
        store=True,
    )

    is_active = fields.Boolean(
        string='Currently Active',
        compute='_compute_is_active',
         
    )

    next_electric_recharge = fields.Date(
        string='Next Electric Recharge',
        compute='_compute_next_electric_recharge',
        store=True,
    )

    # =========================================================
    # Compute Methods
    # =========================================================

    @api.depends('maintenance_request_ids')
    def _compute_maintenance_count(self):
        for record in self:
            record.maintenance_count = len(record.maintenance_request_ids)

    @api.depends('start_date', 'end_date')
    def _compute_duration_months(self):
        """Calculate lease duration in months."""
        for record in self:
            if record.start_date and record.end_date:
                delta = relativedelta(
                    record.end_date,
                    record.start_date,
                )

                record.duration_months = (
                    delta.years * 12 + delta.months
                )
            else:
                record.duration_months = 0

    @api.depends('start_date', 'end_date', 'state')
    def _compute_is_active(self):
        """Check if lease is currently active"""
        today = fields.Date.today()
        for record in self:
            if record.state == 'active' and record.start_date and record.end_date:
                record.is_active = record.start_date <= today <= record.end_date
            else:
                record.is_active = False

    @api.depends('start_date')
    def _compute_next_electric_recharge(self):
        for record in self:
            if record.start_date:
                record.next_electric_recharge = (
                    record.start_date + relativedelta(months=1)
                )
            else:
                record.next_electric_recharge = False

    @api.onchange('property_id')
    def _onchange_property_id(self):
        """Set the monthly rent from the selected property and validate availability."""
        if not self.property_id:
            return

        if not self.property_id.available:
            raise ValidationError(
                "The selected property is not available."
            )

        self.monthly_rent = self.property_id.price or 0.0
        self.deposit_paid = self.property_id.price*0.1

    # =========================================================
    # Lease Actions
    # =========================================================

    def activate_lease(self):
        for record in self:
            record.write({
                'state': 'active',
            })

    def draft_lease(self):
        for record in self:
            record.write({
                'state': 'draft',
            })

    def cancel_lease(self):
        for record in self:
            record.write({
                'state': 'cancelled',
            })

    # =========================================================
    # Maintenance Actions
    # =========================================================

    def action_view_maintenance(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Requests',
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form',
            'domain': [
                ('lease_id', '=', self.id),
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

    # =========================================================
    # Create / Copy / Delete
    # =========================================================

    # @api.model_create_multi
    # def create(self, vals_list):
    #     sequence = self.env['ir.sequence']

    #     for vals in vals_list:
    #         if not vals.get('name') or vals.get('name') == 'New':
    #             vals['name'] = (
    #                 sequence.next_by_code('real_estate.lease')
    #                 or 'New'
    #             )

    #     return super().create(vals_list)

    def copy(self, default=None):
        default = dict(default or {})

        default['name'] = (
            self.env['ir.sequence'].next_by_code(
                'real_estate.lease'
            )
            or 'New'
        )

        return super().copy(default)

    def unlink(self):
        if not self.env.user.has_group(
            'real_estate.group_lease_manager'
        ):
            raise UserError(
                _('Only Lease Managers can delete leases.')
            )

        return super().unlink()

    @api.depends(
        'maintenance_request_ids.actual_cost',
        'maintenance_request_ids.issue_type',
    )
    def _compute_maintenance_costs(self):
        for record in self:
            costs = {
                'plumbing': 0.0,
                'electrical': 0.0,
                'air_condition': 0.0,
                'appliance': 0.0,
                'other': 0.0,
            }

            for maintenance in record.maintenance_request_ids:
                issue_type = maintenance.issue_type

                if issue_type:
                    costs[issue_type] = (
                        costs.get(issue_type, 0.0)
                        + maintenance.actual_cost
                    )

            record.plumbing_cost = costs['plumbing']
            record.electrical_cost = costs['electrical']
            record.air_condition_cost = costs['air_condition']
            record.appliance_cost = costs['appliance']
            record.other_cost = costs['other']
            record.total_cost = sum(costs.values())
            
                
    def _cron_auto_expire_leases(self):
        """Scheduled action - expire leases whose end date has passed"""
        today = fields.Date.today()
        expired_leases = self.search([
            ('end_date', '<', today),
        ])
        for lease in expired_leases:
            lease.write({'state': 'expired'})
            
            
        # === VALIDATION ===
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Ensure end date is after start date"""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date <= record.start_date:
                    raise ValidationError("End date must be after start date")
    
    
    @api.constrains('deposit_paid','monthly_rent')
    def _check_price(self):
        for record in self:
            if record.deposit_paid and record.monthly_rent:
                if record.deposit_paid > record.monthly_rent:
                    raise ValidationError("Deposit can not be grater than price ")
    


