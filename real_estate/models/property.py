
from odoo import models, fields


class Property(models.Model):
    _name = 'real_estate.property'
    _description = 'Real Estate Property'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Property Name',
        required=True,
        index=True
    )

    description = fields.Text(
        string='Description'
    )

    price = fields.Float(
        string='Monthly Rent',
        required=True
    )

    bedrooms = fields.Integer(
        string='Bedrooms',
        required=True
    )

    available = fields.Boolean(
        string='Available',
        default=True,
        index=True
    )

    image = fields.Binary(
        string='Property Image'
    )

    agent_id = fields.Many2one(
        'res.users',
        string='Sales Person'
    )

    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),
    ], string='Property Type', required=True)

    deposit = fields.Float(
        string='Deposit',
        required=True
    )

    lease_ids = fields.One2many(
        'real_estate.lease',
        'property_id',
        string='Leases'
    )

    def mark_as_occupied(self):
        for record in self:
            record.write({
                'available': False,
                'price': record.price + 1000,
            })

    def mark_as_available(self):
        for record in self:
            record.write({
                'available': True,
            })

    def add_text(self):
        for record in self:
            current_description = record.description or ''
            record.write({
                'description': current_description + ' Description'
            })

    def increse_deposit(self):
        for record in self:
            record.write({
                'deposit': record.deposit + 1000
            })

    def add_bedroom(self):
        for record in self:
            record.write({
                'bedrooms': record.bedrooms + 1
            })

    def mark_as_villa(self):
        for record in self:
            if record.available:
                record.write({
                    'property_type': 'villa'
                })

    def get_agent_name(self):
        for record in self:
            record.write({
                'description': record.agent_id.name
            })

