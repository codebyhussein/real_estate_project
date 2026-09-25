from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class RealEstateMaintainancePortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):

        values = super()._prepare_home_portal_values(counters)

        if "maintainance_request_count" in counters:

            count = request.env[
                'maintenance.request'
            ].sudo().search_count([
                ('assigned_to', '=', request.env.user.id)
            ])

            values['maintainance_request_count'] = count

        return values


    def _prepare_portal_layout_values(self):

        values = super()._prepare_portal_layout_values()

        maintainance_request_count = request.env[
            'maintenance.request'
        ].sudo().search_count([
            ('assigned_to', '=', request.env.user.id)
        ])

        values.update({
            'maintainance_request_count': maintainance_request_count,
        })

        return values


    @http.route(
        ['/my/requests', '/my/requests/page/<int:page>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_my_requests(self, page=1, **kw):

        values = self._prepare_portal_layout_values()

        maintainance_requests = request.env[
            'maintenance.request'
        ].sudo().search([
            ('assigned_to', '=', request.env.user.id)
        ], order='create_date desc')

        values.update({
            'maintainance_requests': maintainance_requests,
        })

        return request.render(
            'real_estate.portal_my_requests',
            values
        )
