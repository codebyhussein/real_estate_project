

import odoo
from odoo import http, fields
from odoo.http import request
import json
from functools import wraps


class RealEstateAPI(http.Controller):

    @http.route('/api/properties/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_property(self, **kwargs):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get(
            'Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        try:
            params = kwargs
            print(request.env.user.name)
            # if not request.env.user.has_group('real_estate.group_property_manager'):
            #     return {
            #         'status': 'error',
            #         'message': 'You do not have permission to create properties'
            #     }
            # Validate required fields
            if not params.get('name') or not params.get('price'):
                return {
                    'status': 'error',
                    'message': 'Name and price are required'
                }

            # Create property
            property_obj = request.env['real_estate.property'].sudo().create({
                'name': params.get('name'),
                'price': params.get('price'),
                'bedrooms': params.get('bedrooms', 0),
                'property_type': params.get('property_type', 'house'),
                'external_id': params.get('external_id'),
                'deposit': params.get('deposit'),
            })

            return {
                'status': 'success',
                'message': 'Property created successfully',
                'data': {
                    'property_id': property_obj.id,
                    'name': property_obj.name,
                    'external_id': property_obj.external_id
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

# api for tenant
    @http.route('/api/tenant/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_tenant(self, **kwargs):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get(
            'Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        try:
            params = kwargs
            print(request.env.user.name)
            print(request.env.user.id)

            if not params.get('name') or not params.get('email'):
                return {
                    'status': 'error',
                    'message': 'Name and email are required'
                }

            tenant_obj = request.env['real_estate.tenant'].sudo().create({
                'name': params.get('name'),
                'email': params.get('email'),
                'phone': params.get('phone'),

                'external_id': params.get('external_id'),
                'created_by_api': True

            })

            return {
                'status': 'success',
                'message': 'Tenant created successfully',
                'data': {

                    'name': tenant_obj.name,
                    'external_id': tenant_obj.external_id,
                    'phone': tenant_obj.phone
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/tenant/update', type='json', auth='none', methods=['PUT'], csrf=False)
    def update_tenant(self, **kwargs):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get(
            'Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        try:
            params = kwargs

            tenant_obj = request.env['real_estate.tenant'].sudo().browse(
                params.get('id')
            )

            if not tenant_obj.exists():
                return {
                    'status': 'error',
                    'message': 'Tenant not found',
                }
            if not tenant_obj.active:
                return {
                    'status': 'error',
                    'message': 'Tenant is not active',
                }
            tenant_obj.write({
                'phone': params.get('phone'),
            })

            return {
                'status': 'success',
                'message': 'Tenant updated successfully',
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
            }

# create lead
    @http.route(
        '/api/leads/create',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False
    )
    def create_lead(self, **kwargs):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get(
            'Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        try:
            params = kwargs

            print(request.env.user.name)

            # Validate required fields
            if (
                not params.get('name')
                or not params.get('email_from')
                or not params.get('phone')
                or not params.get('property_type')
            ):
                return {
                    'status': 'error',
                    'message': 'some required data is not set'
                }

            # Create lead
            lead_obj = request.env['crm.lead'].sudo().create({
                'name': params.get('name'),
                'email_from': params.get('email_from'),
                'phone': params.get('phone'),
                'property_type': params.get('property_type'),

            })

            return {
                'status': 'success',
                'message': 'lead created successfully',
                'data': {
                    'name': lead_obj.name,

                    'phone': lead_obj.phone,
                    'property_type': lead_obj.property_type,
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    @http.route('/api/tenants/update/<int:tenant_id>', type='http', auth='none', methods=['PUT'], csrf=False)
    def update_tenant(self, tenant_id):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get(
            'Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        tenant_obj = request.env['real_estate.tenant'].sudo().browse(tenant_id)
        # print(tenant_obj.name)
        if not tenant_obj.exists():
            return request.make_json_response(
                {'status': 'error',
                 'message': 'Tenant not found'},
                status=404
            )

        params = request.httprequest.get_json(silent=True)

        tenant_obj.write(params)
        return request.make_json_response({'status': 'success',
                                           'tenant_id': tenant_obj.id}
                                          )

        # update the thp property

    @http.route('/api/properties/update/<int:property_id>', type='http', auth='none', methods=['PUT'], csrf=False)
    def update_property(self, property_id):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get(
            'Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        property_obj = request.env['real_estate.property'].sudo().browse(
            property_id)
        # print(property_obj.name)
        if not property_obj.exists():
            return request.make_json_response(
                {'status': 'error',
                    'message': 'Property not found'},
                status=404
            )

        params = request.httprequest.get_json(silent=True)

        property_obj.write(params)
        return request.make_json_response({'status': 'success',
                                           'property_id': property_obj.id,

                                           'data': property_obj.read()[0]}
                                          )


#  Get List lease


    @http.route('/api/list_leases', type='http', auth='none', methods=['GET'], csrf=False)
    def list_leases(self):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get(
            'Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)
        date_from = request.httprequest.args.get('date_from')
        date_to = request.httprequest.args.get('date_to')
        if not date_from or not date_to:
            return request.make_json_response(
                {'status': 'error',
                 'message': 'date_from and date_to are required'},
                status=400
            )

        try:
            print('date_from 1:', date_from)
            date_from = fields.Date.to_date(date_from)
            date_to = fields.Date.to_date(date_to)
            print('date_from 2:', date_from)

        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers={'Content-Type': 'application/json'}
            )

        if date_from > date_to:
            return request.make_response(
                json.dumps({'status': 'error',
                            'message': 'date_from must be before date_to'}),
                headers={'Content-Type': 'application/json'}
            )

        leases = request.env['real_estate.lease'].sudo().search([
            ('start_date', '<=', date_to),
            ('end_date', '>=', date_from),
        ])
        return request.make_response(
            json.dumps({
                'status': 'success',
                'data': [{
                    'id': lease.id,
                    'name': lease.name,
                    'tenant': lease.tenant_id.name,
                    'property': lease.property_id.name,
                    'start_date': fields.Date.to_string(lease.start_date),
                    'end_date': fields.Date.to_string(lease.end_date),
                    'monthly_rent': lease.monthly_rent,
                    'state': lease.state,
                } for lease in leases],
            }),
            headers={'Content-Type': 'application/json'}
        )


#  Get List lease by tenant id


    @http.route('/api/tenants/leases/<int:tenant_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def list_leases(self, tenant_id):
        TOKEN = 'cacb064fd72c08b445959768'
        authorization_token = request.httprequest.headers.get(
            'Authorization', '')
        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response({'status': 'error', 'message': 'Unauthorized'}, status=401)

        leases = request.env['real_estate.lease'].sudo().search([
            ('tenant_id', '=', tenant_id),

        ])
        if not leases:
            return request.make_response(
                json.dumps({
                    'status': 'error',
                    'message': 'No leases found for this tenant',
                    'data': [

                    ]
                }),
                headers={'Content-Type': 'application/json'}
            )

        lease_count = len(leases)

        return request.make_response(
            json.dumps({
                'status': 'success',
                'lease_count': lease_count,
                'data': [{
                    'id': lease.id,
                    'name': lease.name,
                    'tenant': lease.tenant_id.name,
                    'property': lease.property_id.name,
                    'start_date': fields.Date.to_string(lease.start_date),
                    'end_date': fields.Date.to_string(lease.end_date),
                    'monthly_rent': lease.monthly_rent,
                    'state': lease.state,
                } for lease in leases],
            }),
            headers={'Content-Type': 'application/json'}
        )

    #     #  create lease and tenant if not exist and property exist

    @http.route(
        '/api/leases/create',
        type='json',
        auth='none',
        methods=['POST'],
        csrf=False
    )
    def create_lease(self, **kwargs):

        TOKEN = 'cacb064fd72c08b445959768'

        authorization_token = request.httprequest.headers.get(
            'Authorization',
            ''
        )

        if authorization_token != f'Bearer {TOKEN}':
            return request.make_json_response(
                {
                    'status': 'error',
                    'message': 'Unauthorized'
                },
                status=401
            )

        try:
            params = kwargs

            required_fields = (
                'name', 'email', 'property_id', 'monthly_rent',
                'start_date', 'end_date',
            )
            missing_fields = [
                field for field in required_fields
                if params.get(field) is None or params.get(field) == ''
            ]
            if missing_fields:
                return {
                    'status': 'error',
                    'message': 'Required fields are missing: '
                    + ', '.join(missing_fields),
                }

            property_obj = request.env[
                'real_estate.property'
            ].sudo().browse(params.get('property_id')).exists()
            if not property_obj:
                return {
                    'status': 'error',
                    'message': 'Property not found',
                }

            with request.env.cr.savepoint():
                tenant_obj = request.env[
                    'real_estate.tenant'
                ].sudo().create({
                    'name': params.get('name'),
                    'email': params.get('email'),
                    'phone': params.get('phone'),
                    'property_type': property_obj.property_type,
                    'external_id': params.get('external_id'),
                    'created_by_api': True,
                })

                lease_obj = request.env[
                    'real_estate.lease'
                ].sudo().create({
                    'property_id': property_obj.id,
                    'tenant_id': tenant_obj.id,
                    'monthly_rent': params.get('monthly_rent'),
                    'start_date': params.get('start_date'),
                    'end_date': params.get('end_date'),
                })

            return {
                'status': 'success',
                'message': 'Lease created successfully',
                'data': {
                    'lease_id': lease_obj.id,
                    'tenant_id': tenant_obj.id,
                    'tenant_name': tenant_obj.name,
                    'tenant_email': tenant_obj.email,
                    'tenant_phone': tenant_obj.phone,
                    'property_id': lease_obj.property_id.id,
                    'lease_reference': lease_obj.name,
                    'monthly_rent': lease_obj.monthly_rent,
                    'start_date': lease_obj.start_date,
                    'end_date': lease_obj.end_date,
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
