# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"

    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        inverse_name="fsm_recurring_id",
        readonly=True,
    )
    fsm_order_by_year_count = fields.Integer(
        "Theoric Yearly order count",
        compute="_compute_tehoric_order_count",
        help="We need the theorical count of order by year"
        " To compute a avarage price for each order if the invoice is based on the number of realised order."
        " In deed, for some frequencies, the numbre of orders is depending on month. Some month we have "
        " 5 monday and 4 for others. The price payed each month is the same for each month "
        "despite the difference in the theoric number of orders.",
        store=True,
    )
    fsm_order_by_month_count = fields.Integer(
        "Theoric Yearly order count", compute="_compute_tehoric_order_count", store=True
    )

    def _prepare_order_values(self, date=None):
        res = super()._prepare_order_values(date)
        res["contract_line_id"] = self.contract_line_id.id
        return res

    @api.depends("fsm_frequency_set_id.fsm_frequency_ids")
    def _compute_tehoric_order_count(self):
        date_start = fields.datetime.today()
        date_start.replace(**{"day": 1, "month": 1})
        date_end = fields.datetime.today()
        date_end.replace(**{"day": 31, "month": 12})
        for recuring in self:
            rrules = recuring.fsm_frequency_set_id._get_rruleset(
                dtstart=date_start, until=date_end
            )
            recuring.fsm_order_by_year_count = len([date for date in rrules])
            recuring.fsm_order_by_month_count = (
                recuring.fsm_order_by_year_count / 12.0
            )  # number of month a year
