from odoo import fields, models


class FSMRoute(models.Model):
    _inherit = 'fsm.route'

    name = fields.Char(translate=True)
    route_type = fields.Selection([
        ('visit', 'Site Visit'),
        ('maintenance', 'Maintenance'),
        ('installation', 'Installation'),
    ], string='Route Type', default='visit')
