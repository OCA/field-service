# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE to apply the repair order template on the related repair order
        records = super().create(vals_list)
        records._apply_repair_order_template()
        return records

    def write(self, vals):
        # OVERRIDE to apply the repair order template on the related repair order
        res = super().write(vals)
        if "template_id" in vals:
            self._apply_repair_order_template()
        return res

    def _onchange_template_id(self):
        res = super()._onchange_template_id()
        self._apply_repair_order_template()
        return res

    def _apply_repair_order_template(self):
        """Apply the Repair Order Template on the related repair order"""
        for rec in self:
            if (
                rec.repair_id
                and rec.repair_id.state == "draft"
                and rec.template_id.repair_order_template_id
            ):
                rec.repair_id.repair_order_template_id = (
                    rec.template_id.repair_order_template_id
                )
                rec.repair_id._onchange_repair_order_template_id()
