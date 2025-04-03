# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrderReportWizard(models.TransientModel):
    _name = "fsm.order.report.wizard"
    _description = "Field Service Order Report Wizard"
    _inherit = "fsm.order.report.mixin"

    template_id = fields.Many2one("fsm.order.report.template", string="Template")

    @api.depends("template_id")
    def _compute_person_id(self):
        for item in self:
            template = item.template_id
            item.vehicle_id = template.vehicle_id or False
            item.dayroute_id = template.dayroute_id or False
            item.fsm_route_id = template.fsm_route_id or False
            item.person_id = template.person_id or False
            item.location_id = template.location_id or False
            item.stage_id = template.stage_id or False
            item.tag_ids = template.tag_ids.ids or False
            item.category_ids = template.category_ids or False
            item.type = template.type or False
            item.team_id = template.team_id or False
            item.field_ids = template.field_ids or False

    def action_print_report(self):
        data = {
            "company_id": self.company_id.id,
            "vehicle_id": self.vehicle_id.id,
            "dayroute_id": self.dayroute_id.id,
            "fsm_route_id": self.fsm_route_id.id,
            "person_id": self.person_id.id,
            "location_id": self.location_id.id,
            "stage_id": self.stage_id.id,
            "tag_ids": self.tag_ids.ids,
            "category_ids": self.category_ids.ids,
            "type": self.type.id,
            "team_id": self.team_id.id,
            "field_ids": [
                (field.field_description, field.name) for field in self.field_ids
            ],
        }
        return self.env.ref(
            "fieldservice_order_report.action_report_fsm_order"
        ).report_action([], data=data)
