# Copyright (C) 2021 Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools


class Meeting(models.Model):
    _inherit = "calendar.event"

    fsm_order_id = fields.One2many(
        string="Order id",
        comodel_name="fsm.order",
        inverse_name="calendar_event_id",
    )

    def _update_fsm_order_date(self):
        self.ensure_one()
        to_apply = {}
        to_apply["scheduled_date_start"] = self.start
        to_apply["scheduled_duration"] = self.duration
        self.fsm_order_id.write(to_apply)

    def _update_fsm_assigned(self):
        # update back fsm_order when an attenndee is member of a team
        self.ensure_one()
        for partner in self.partner_ids.filtered("fsm_person"):
            self.fsm_order_id.person_id = self.env["fsm.person"].search(
                [("partner_id", "=", partner.id)], limit=1
            )
            break

    def _update_fsm_order_description(self):
        self.fsm_order_id.description = tools.html2plaintext(self.description or "")

    def write(self, values):
        res = super().write(values)
        if values.keys() & {
            "start",
            "duration",
            "partner_ids",
            "description",
        } and not self.env.context.get("recurse_order_calendar"):
            for event in self.filtered("fsm_order_id").with_context(
                recurse_order_calendar=True
            ):
                if "start" in values or "duration" in values:
                    event._update_fsm_order_date()
                if "partner_ids" in values:
                    event._update_fsm_assigned()
                if "description" in values:
                    event._update_fsm_order_description()
        return res
