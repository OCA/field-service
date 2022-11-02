# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    order_activity_ids = fields.One2many(
        "fsm.activity",
        "fsm_order_id",
        "Order Activities",
        compute="_compute_order_activity_ids",
        store=True,
    )

    @api.depends("template_id")
    def _compute_order_activity_ids(self):
        for rec in self:
            # Clear existing activities
            if not rec.template_id:
                continue

            activity_list = [(5, 0, 0)]
            activity_list.extend(
                (
                    0,
                    0,
                    {
                        "name": temp_activity.name,
                        "required": temp_activity.required,
                        "ref": temp_activity.ref,
                        "state": temp_activity.state,
                    },
                )
                for temp_activity in rec.template_id.temp_activity_ids
            )

            rec.order_activity_ids = activity_list

    @api.model_create_multi
    def create(self, vals):
        """Update Activities for FSM orders that are generate from SO"""
        orders = super(FSMOrder, self).create(vals)
        for order in orders:
            order._onchange_template_id()
        return orders

    def action_complete(self):
        res = super().action_complete()
        for activity in self.order_activity_ids:
            if activity.required and activity.state == "todo":
                raise ValidationError(
                    _(
                        "You must complete activity '%s' before \
                    completing this order."
                    )
                    % activity.name
                )
        self.activity_ids._action_done()
        return res
