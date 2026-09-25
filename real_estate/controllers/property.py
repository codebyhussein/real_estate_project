from odoo import http
from odoo.http import request


class PropertyController(http.Controller):
    
    

    @http.route(
        '/properties',
        type='http',
        auth='public',
        website=True
    )
    def properties(self, **kwargs):

        properties = request.env['real_estate.property'].sudo().search([
            ('available', '=', True)
        ])

        return request.render(
            'real_estate.property_list',
            {
                'properties': properties,
            }
        )
        
        
        
    @http.route(
    '/property/<int:property_id>',
    type='http',
    auth='public',
    website=True
)
    def property_details(self, property_id, **kwargs):

        property_record = request.env[
            'real_estate.property'
        ].sudo().browse(property_id)

        if not property_record.exists():
            return request.not_found()

        return request.render(
            'real_estate.property_details',
            {
                'property': property_record,
            }
        )