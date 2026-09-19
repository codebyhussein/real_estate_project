
from re import A


from odoo import models, fields, api
from odoo.exceptions import UserError

class Property(models.Model):
    _name = 'real_estate.property'
    _description = 'Real Estate Property'

    name = fields.Char(string='Property Name', required=True, index=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Monthly Rent', required=True)    
    bedrooms = fields.Integer(string='Bedrooms', required=True)
    available = fields.Boolean(string='Available', default=True, index=True)   

    agent_id = fields.Many2one('res.users', string='Sales Person',)
    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),
    ], string='Property Type', required=True)
    deposit = fields.Float(required=True)


    def mark_as_occupied(self):
        """Mark property as no longer available"""
        for record in self:
            record.write({'available': False, 'price': record.price + 1000})
    
    def mark_as_available(self):
        """Mark property as available"""
        for record in self:
            record.write({'available': True})



    def add_text(self):
        """Add text to the description field"""
        for record in self:
            record.write({'description': (record.description + ' Description ')})

    def increse_deposit(self):
        """Increase deposit by 10%"""
        for record in self:
            record.write({'deposit': record.deposit +1000})



    def add_bedroom(self):
        """Add a bedroom to the property"""
        for record in self:
            record.write({'bedrooms': record.bedrooms + 1})


    def mark_as_villa(self):
        """Change the property type to Villa"""
        for record in self:
            if record.available:
                record.write({'property_type': 'villa'})


    def get_agent_name(self):
         for record in self:

                record.write({'description': record.agent_id.name})  # pyright: ignore[reportAttributeAccessIssue]

    

    # def write(self, vals):
    #      if vals.get('available')==False :
    #         raise UserError("You cannot edit bedrooms when they are unavailable.")
    #      return super(Property,self).write(vals)

    def action_open_lease_wizard(self):
       self.ensure_one()

       return {
        'type': 'ir.actions.act_window',
        'name': 'Create Lease',
        'res_model': 'real_estate.lease.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_property_id': self.id,
            'default_monthly_rent': self.price,
            'default_user_id': self.env.user.id,
        },
    }