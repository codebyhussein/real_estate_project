# -*- coding: utf-8 -*-
{
    'name': "Real Estate Managment",

    'summary': """
A complete Real Estate Management module for managing properties, units, owners, and tenants efficiently.
Track property availability, sales, rentals, contracts, and related financial transactions in one place.
Designed to simplify real estate operations and provide clear, organized property management workflows.
""",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm', 'mail','website'],

# always loaded
'data': [
    # Security
    'security/security_rules.xml',
    'security/ir.model.access.csv',

    # Data
    'data/ir_sequence_data.xml',
    'data/lease_cron.xml',

    # Wizards
    'wizard/maintenance.xml',
    'wizard/lease_wizard.xml',
    'wizard/tenant_wizard.xml',

    # Views
    'views/property_views.xml',
    'views/property_inherit.xml',

    'views/lease_view.xml',
    'views/lease_inherit.xml',

    'views/tenant_view.xml',

    'views/crm_led_view.xml',
    'views/portal_templates_lease.xml',
    'views/portal_templates_maintainance.xml',
    'views/portal_templates_property.xml',
    'views/maintanace_view.xml',
    'views/property_templates_website.xml',
    'data/mail_template_data.xml',
    'views/res_partner.xml',
    'views/payment.xml',

    # Menus
    'views/menu.xml',
],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',

    ],
} # type: ignore

