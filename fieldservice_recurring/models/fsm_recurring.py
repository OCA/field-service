# Copyright (C) 2019 Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rruleset

from odoo import _, api, fields, models


class FSMRecurringOrder(models.Model):
    _name = "fsm.recurring"
    _description = "Recurring Field Service Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_team_id(self):
        return self.env["fsm.team"].search(
            [["company_id", "in", (self.env.company.id, False)]],
            limit=1,
            order="sequence",
        )

    name = fields.Char(
        required=True,
        index=True,
        copy=False,
        default=lambda self: _("New"),
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("progress", "In Progress"),
            ("suspend", "Suspended"),
            ("close", "Closed"),
        ],
        readonly=True,
        default="draft",
        tracking=True,
    )
    fsm_recurring_template_id = fields.Many2one(
        "fsm.recurring.template",
        "Recurring Template",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    location_id = fields.Many2one(
        "fsm.location", string="Location", index=True, required=True
    )
    description = fields.Text()
    fsm_frequency_set_id = fields.Many2one(
        "fsm.frequency.set",
        "Frequency Set",
    )
    scheduled_duration = fields.Float(help="Scheduled duration of the work in hours")

    start_date = fields.Datetime()
    end_date = fields.Datetime(help="Recurring orders will not be made after this date")
    max_orders = fields.Integer(
        string="Maximum Orders", help="Maximium number of orders that will be created"
    )
    fsm_order_template_id = fields.Many2one(
        "fsm.template",
        string="Order Template",
        help="This is the order template that will be recurring",
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.user.company_id
    )
    fsm_order_ids = fields.One2many(
        "fsm.order", "fsm_recurring_id", string="Orders", copy=False
    )
    fsm_order_count = fields.Integer("Orders Count", compute="_compute_order_count")
    team_id = fields.Many2one(
        "fsm.team",
        string="Team",
        default=lambda self: self._default_team_id(),
        index=True,
        required=True,
        tracking=True,
    )
    person_id = fields.Many2one(
        "fsm.person", string="Assigned To", index=True, tracking=True
    )
    equipment_ids = fields.Many2many("fsm.equipment")

    @api.depends("fsm_order_ids")
    def _compute_order_count(self):
        data = self.env["fsm.order"].read_group(
            [
                ("fsm_recurring_id", "in", self.ids),
                ("stage_id", "!=", self.env.ref("fieldservice.fsm_stage_cancelled").id),
            ],
            ["fsm_recurring_id"],
            ["fsm_recurring_id"],
        )
        count_data = {
            item["fsm_recurring_id"][0]: item["fsm_recurring_id_count"] for item in data
        }
        for recurring in self:
            recurring.fsm_order_count = count_data.get(recurring.id, 0)

    @api.onchange("fsm_recurring_template_id")
    def onchange_recurring_template_id(self):
        if not self.fsm_recurring_template_id:
            return
        self.update(self.populate_from_template())

    def populate_from_template(self, template=False):
        if not template:
            template = self.fsm_recurring_template_id
        return {
            "fsm_frequency_set_id": template.fsm_frequency_set_id,
            "max_orders": template.max_orders,
            "description": template.description,
            "fsm_order_template_id": template.fsm_order_template_id,
            "scheduled_duration": template.fsm_order_template_id.duration,
            "company_id": template.company_id,
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "fsm.recurring"
                ) or _("New")
        return super(FSMRecurringOrder, self).create(vals_list)

    def action_start(self):
        for rec in self:
            if not rec.start_date:
                rec.start_date = datetime.now()
            rec.write({"state": "progress"})
            rec._generate_orders()

    def action_suspend(self):
        for order in self.fsm_order_ids.filtered(
            lambda o: o.stage_id.is_closed is False
        ):
            order.action_cancel()
        return self.write({"state": "suspend"})

    def _get_rruleset(self):
        self.ensure_one()
        ruleset = rruleset()
        if self.state != "progress" or not self.fsm_frequency_set_id:
            return ruleset
        # set next_date which is used as the rrule 'dtstart' parameter
        next_date = self.start_date
        last_order = self.env["fsm.order"].search(
            [
                ("fsm_recurring_id", "=", self.id),
                ("stage_id", "!=", self.env.ref("fieldservice.fsm_stage_cancelled").id),
            ],
            offset=0,
            limit=1,
            order="scheduled_date_start desc",
        )
        if last_order:
            next_date = last_order.scheduled_date_start
        # set thru_date to use as rrule 'until' parameter
        days_ahead = self.fsm_frequency_set_id.schedule_days
        request_thru_date = datetime.now() + relativedelta(days=+days_ahead)
        if self.end_date and (self.end_date < request_thru_date):
            thru_date = self.end_date
        else:
            thru_date = request_thru_date
        # use variables to calulate and return the rruleset object
        ruleset = self.fsm_frequency_set_id._get_rruleset(
            dtstart=next_date, until=thru_date
        )
        return ruleset

    def _prepare_order_values(self, date=None):
        self.ensure_one()
        schedule_date = date if date else datetime.now()
        days_early = self.fsm_frequency_set_id.buffer_early
        earliest_date = schedule_date + relativedelta(days=-days_early)
        scheduled_duration = (
            self.scheduled_duration or self.fsm_order_template_id.duration
        )
        return {
            "fsm_recurring_id": self.id,
            "location_id": self.location_id.id,
            "team_id": self.team_id.id,
            "scheduled_date_start": schedule_date,
            "request_early": str(earliest_date),
            "description": self.description,
            "template_id": self.fsm_order_template_id.id,
            "scheduled_duration": scheduled_duration,
            "category_ids": [(6, False, self.fsm_order_template_id.category_ids.ids)],
            "company_id": self.company_id.id,
            "person_id": self.person_id.id,
            "equipment_ids": [(6, 0, self.equipment_ids.ids)],
        }

    def _create_order(self, date):
        self.ensure_one()
        vals = self._prepare_order_values(date)
        order = self.env["fsm.order"].create(vals)
        order._onchange_template_id()
        return order

    def _generate_orders(self):
        """
        create field service orders from self
        up to the max orders allowed by the recurring order
        @return {recordset} orders: all the order objects created
        """
        orders = self.env["fsm.order"]
        for rec in self:
            order_dates = []
            for order in rec.fsm_order_ids:
                if order.scheduled_date_start:
                    order_dates.append(order.scheduled_date_start.date())
            max_orders = rec.max_orders if rec.max_orders > 0 else False
            order_count = rec.fsm_order_count
            for date in rec._get_rruleset():
                if date.date() in order_dates:
                    continue
                if max_orders > order_count or not max_orders:
                    orders |= rec._create_order(date=date)
                    order_count += 1
        return orders

    @api.model
    def _cron_generate_orders(self):
        """
        Executed by Cron task to create field service orders from any
        recurring orders which are in progress, or to renew, and up to
        the max orders allowed by the recurring order
        @return {recordset} orders: all the order objects created
        """
        return (
            self.env["fsm.recurring"]
            .search([("state", "=", "progress")])
            ._generate_orders()
        )

    @api.model
    def _cron_manage_expiration(self):
        """
        Executed by Cron task to put all 'in progress' recurring orders into
        'close' stage if it is after their end date or the max orders have
        been generated.
        """
        to_close = self.env["fsm.recurring"]
        open_rec = self.env["fsm.recurring"].search([("state", "=", "progress")])
        for rec in open_rec:
            if rec.end_date and rec.end_date <= datetime.today():
                to_close += rec
                continue
            if rec.max_orders > 0 and rec.fsm_order_count >= rec.max_orders:
                to_close += rec
        to_close.write({"state": "close"})

    @api.model
    def _cron_scheduled_task(self):
        self._cron_generate_orders()
        self._cron_manage_expiration()
