# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    total_cost = fields.Float(compute="_compute_total_cost")
    bill_to = fields.Selection(
        [("location", "Bill Location"), ("contact", "Bill Contact")],
        required=True,
        default="location",
    )
    customer_id = fields.Many2one(
        "res.partner",
        string="Contact",
        change_default=True,
        index="btree",
        tracking=True,
    )

    def _compute_total_cost(self):
        """To be overridden as needed from other modules"""
        for order in self:
            order.total_cost = 0.0

    @api.onchange("customer_id")
    def _onchange_customer_id_location(self):
        self.location_id = (
            self.customer_id.service_location_id if self.customer_id else False
        )

    def write(self, vals):
        res = super(FSMOrder, self).write(vals)
        for order in self:
            if "customer_id" not in vals and not order.customer_id:
                order.customer_id = order.location_id.customer_id.id
        return res
