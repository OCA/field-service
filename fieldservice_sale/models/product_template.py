# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    service_type = fields.Selection(selection_add=[
        ('field', 'Field Service Orders'),
    ])
    field_service_tracking = fields.Selection([
        ('no', 'Don\'t create order'),
        ('order', 'Create a single order')
    ], string="Field Service Tracking", default="no",
        help="""On Sales order confirmation, this product can generate a field
                service order or field service recurring order.""")
    fsm_order_template_id = fields.Many2one(
        'fsm.template', 'Field Service Order Template',
        help="Select the field service order template to be created")

    @api.onchange('field_service_tracking')
    def _onchange_field_service_tracking(self):
        if self.field_service_tracking != 'order':
            self.fsm_order_template_id = False
