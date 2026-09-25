# -*- coding: utf-8 -*-
# from odoo import http


# class RealEstateProject(http.Controller):
#     @http.route('/real_estate_project/real_estate_project', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/real_estate_project/real_estate_project/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('real_estate_project.listing', {
#             'root': '/real_estate_project/real_estate_project',
#             'objects': http.request.env['real_estate_project.real_estate_project'].search([]),
#         })

#     @http.route('/real_estate_project/real_estate_project/objects/<model("real_estate_project.real_estate_project"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('real_estate_project.object', {
#             'object': obj
#         })
from odoo import http
from odoo.http import request
from werkzeug.urls import url_quote
from odoo.addons.portal.controllers.portal import CustomerPortal # pyright: ignore[missing-import]

class RealEstatePortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(RealEstatePortal, self)._prepare_portal_layout_values()
        tenant = request.env['real_estate.tenant'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        lease_count = 0
        if tenant:
            lease_count = request.env['real_estate.lease'].sudo().search_count([
                ('tenant_id', '=', tenant.id)
            ])
        values.update({
            'lease_count': lease_count,
            'tenant': tenant,
        })
        return values

    @http.route(['/my/leases', '/my/leases/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_leases(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        tenant = values.get('tenant')
        if not tenant:
            values.update({
                'leases': request.env['real_estate.lease'].sudo().browse(),
            })
            return request.render('real_estate.portal_my_leases', values)

        leases = request.env['real_estate.lease'].sudo().search([
            ('tenant_id', '=', tenant.id),
            ('state', '=', 'active')
        ], order='start_date desc')
        values.update({
            'leases': leases,
        })
        return request.render('real_estate.portal_my_leases', values)