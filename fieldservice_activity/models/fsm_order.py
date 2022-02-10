# Copyright (C) 2019, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    order_activity_ids = fields.One2many("fsm.activity", "fsm_order_id", "Activites")

    @api.onchange("template_id")
    def _onchange_template_id(self):
        res = super()._onchange_template_id()
        for rec in self:
            # Clear existing activities
            rec.order_activity_ids = [(5, 0, 0)]
            if rec.template_id:
                activity_list = []
                for temp_activity in rec.template_id.temp_activity_ids:
                    activity_list.append(
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
                    )
                rec.order_activity_ids = activity_list
        return res

    @api.model
    def create(self, vals):
        """Update Activities for FSM orders that are generate from SO"""
        order = super(FSMOrder, self).create(vals)
        order._onchange_template_id()
        return order

    def action_complete(self):
        res = super().action_complete()
        for activity_id in self.order_activity_ids:
            if activity_id.required and activity_id.state == "todo":
                raise ValidationError(
                    _(
                        "You must complete activity '%s' before \
                    completing this order."
                    )
                    % activity_id.name
                )
        for activity_id in self.activity_ids:
            activity_id._action_done()
        return res
