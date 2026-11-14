# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import Command, api, fields, models


class FSMRecurring(models.Model):
    _inherit = "fsm.recurring"

    is_preventive = fields.Boolean(
        string="Preventive Visit",
        help="Fill each generated order with a checklist of the equipments "
        "of the location that are due for a preventive visit.",
    )
    preventive_type_ids = fields.Many2many(
        "fsm.preventive.type",
        string="Visit Types",
        help="Visit types covered by this recurring order. Leave empty for all.",
    )
    preventive_equipment_count = fields.Integer(
        compute="_compute_preventive_equipment_count",
        string="Equipments With Preventive",
    )

    @api.depends("is_preventive", "location_id", "company_id", "preventive_type_ids")
    def _compute_preventive_equipment_count(self):
        for recurring in self:
            preventives = (
                recurring._get_preventives()
                if recurring.is_preventive and recurring.location_id
                else self.env["fsm.equipment.preventive"]
            )
            recurring.preventive_equipment_count = len(preventives.equipment_id)
            recurring.preventive_no_template_count = len(
                preventives.filtered(lambda p: not p.template_id).equipment_id
            )

    preventive_no_template_count = fields.Integer(
        compute="_compute_preventive_equipment_count",
        string="Equipments Without Template",
    )

    def action_view_preventive_no_template(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice.action_fsm_equipment"
        )
        action["domain"] = [
            (
                "id",
                "in",
                self._get_preventives()
                .filtered(lambda p: not p.template_id)
                .equipment_id.ids,
            )
        ]
        return action

    def action_view_preventive_equipments(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice.action_fsm_equipment"
        )
        action["domain"] = [("id", "in", self._get_preventives().equipment_id.ids)]
        return action

    def _get_preventive_equipment_domain(self):
        self.ensure_one()
        return [
            ("current_location_id", "child_of", self.location_id.id),
            ("company_id", "in", [self.company_id.id, False]),
        ]

    def _get_preventives(self):
        """Preventive visits of the equipments covered by this recurring order."""
        self.ensure_one()
        domain = [
            (
                "equipment_id",
                "in",
                self.env["fsm.equipment"]._search(
                    self._get_preventive_equipment_domain()
                ),
            )
        ]
        if self.preventive_type_ids:
            domain.append(("type_id", "in", self.preventive_type_ids.ids))
        return self.env["fsm.equipment.preventive"].search(domain)

    def _get_preventive_horizon(self, date):
        """What is due before the visit that follows ``date`` is included."""
        self.ensure_one()
        following = self.fsm_frequency_set_id._get_rruleset(
            dtstart=date, until=date + relativedelta(years=1)
        ).after(date)
        return (following or date).date()

    def _get_due_preventives(self, date):
        """Preventive visits due by the visit of ``date``, in checklist order.

        What is already listed in an earlier open visit is expected to be done
        then, so its due date is projected from that visit.
        """
        self.ensure_one()
        horizon = self._get_preventive_horizon(date)
        planned = {}
        open_lines = self.env["fsm.order.equipment.line"].search(
            [
                ("order_id.fsm_recurring_id", "=", self.id),
                ("order_id.stage_id.is_closed", "=", False),
                ("order_id.scheduled_date_start", "<", date),
                ("preventive_id", "!=", False),
                ("state", "=", "pending"),
            ]
        )
        for line in open_lines:
            visit = line.order_id.scheduled_date_start.date()
            planned[line.preventive_id] = max(
                planned.get(line.preventive_id, visit), visit
            )
        due = self.env["fsm.equipment.preventive"]
        for preventive in self._get_preventives():
            next_date = preventive.next_date
            if preventive in planned:
                next_date = planned[preventive] + relativedelta(
                    months=preventive.interval
                )
            if next_date <= horizon:
                due |= preventive
        return due.sorted(lambda preventive: preventive._preventive_sort_key())

    def _prepare_order_values(self, date=None):
        vals = super()._prepare_order_values(date=date)
        if self.is_preventive:
            preventives = self._get_due_preventives(vals["scheduled_date_start"])
            vals["equipment_ids"] = [Command.clear()]
            vals["equipment_line_ids"] = [
                Command.create(
                    {
                        "equipment_id": preventive.equipment_id.id,
                        "preventive_id": preventive.id,
                        "template_id": preventive.template_id.id,
                        "sequence": sequence,
                    }
                )
                for sequence, preventive in enumerate(preventives, start=1)
            ]
            order_type = preventives.type_id.order_type_id
            if len(preventives.type_id) == 1 and order_type:
                vals["type"] = order_type.id
        return vals
