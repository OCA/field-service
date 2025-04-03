# Copyright 2025 Antoni Marroig(APSL-Nagarro)<amarroig@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ReportFSMOrder(models.AbstractModel):
    _name = "report.fieldservice_order_report.report_fsm_order"
    _description = "Fieldservice Order Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        FieldServiceOrder = self.env["fsm.order"]
        field_ids = data["field_ids"]
        if not field_ids:
            fields = self.env["ir.model.fields"].search([("model", "=", "fsm.order")])
            field_ids = [
                (fields.filtered(lambda x: x.name == "name").field_description, "name"),
                (
                    fields.filtered(
                        lambda x: x.name == "location_id"
                    ).field_description,
                    "location_id",
                ),
                (
                    fields.filtered(
                        lambda x: x.name == "fsm_route_id"
                    ).field_description,
                    "fsm_route_id",
                ),
                (
                    fields.filtered(lambda x: x.name == "person_id").field_description,
                    "person_id",
                ),
                (
                    fields.filtered(lambda x: x.name == "vehicle_id").field_description,
                    "vehicle_id",
                ),
            ]
        domain = []
        for field in data:
            if data[field] and field in self.env["fsm.order"].fields_get():
                domain.append(
                    (
                        field,
                        "in" if isinstance(type(data[field]), list) else "=",
                        data[field],
                    )
                )
        return {"orders": FieldServiceOrder.search(domain), "fields": field_ids}
