# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    sale_order_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="fsm_order_id",
        string="Generated Sale Orders",
        help="Sale Orders Generated from this Service Order",
    )

    def _get_generated_order_context(self):
        return {
            "default_fsm_order_id": self.id,
            "default_partner_id": self.location_id.partner_id.id,
            "default_company_id": self.company_id.id,
            "company_id": self.company_id.id,
        }

    def action_generate_sale_order(self):
        action = self.env.ref('sale.action_quotation_form')
        result = action.read()[0]
        create_quotation = self.env.context.get('create_quotation', False)
        # override the context to get rid of the default filtering
        result['context'] = self._get_generated_order_context()
        # choose the view_mode accordingly
        if len(self.sale_order_ids) > 1 and not create_quotation:
            result['domain'] = "[('id', 'in', {})]".format(
                self.sale_order_ids.ids)
        elif not create_quotation:
                result['res_id'] = self.sale_order_ids.id or False
        result['context']['default_origin'] = self.name
        return result
