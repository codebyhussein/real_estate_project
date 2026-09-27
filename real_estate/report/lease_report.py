from datetime import datetime, timedelta

from odoo import api, models


class LeaseReportSummary(models.AbstractModel):
    _name = 'report.real_estate.report_lease_summary'
    _description = 'Lease Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Prepare the lease summary report data."""
        leases = self.env['real_estate.lease'].browse(docids)

        total_leases = len(leases)
        active_leases = len(leases.filtered(lambda lease: lease.state == 'active'))
        active_rate = (
            (active_leases / total_leases * 100) if total_leases else 0
        )

        six_months_ago = datetime.now() - timedelta(days=180)
        maintenance_costs = {}
        maintenance_by_lease = {lease.id: [] for lease in leases}
        for lease in leases:
            maintenance = self.env['maintenance.request'].search([
                ('lease_id', '=', lease.id),
                # ('completion_date', '>=', six_months_ago),
            ])
            maintenance_costs[lease.id] = sum(maintenance.mapped('actual_cost'))
            maintenance_by_lease[lease.id] = maintenance

        payments_by_lease = {lease.id: [] for lease in leases}
        payments = self.env['lease.payment'].search([
            ('lease_id', 'in', leases.ids),
        ], order='lease_id, due_date desc, id desc')
        
        
        for payment in payments:
            payments_by_lease.setdefault(payment.lease_id.id, []).append(payment)

        return {
            'doc_ids': docids,
            'doc_model': 'real_estate.lease',
            'docs': leases,
            'active_rate': active_rate,
            'maintenance_costs': maintenance_costs,
            'maintenance_by_lease': maintenance_by_lease,
            'payments_by_lease': payments_by_lease,
            'report_date': datetime.now(),
        }