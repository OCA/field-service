# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    request_ids = fields.One2many(
        "maintenance.request", "fsm_order_id", string="Maintenance Request"
    )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            # if FSM order with type maintenance is created then
            # create maintenance requests for every equipment in the order
            if order.type.internal_type == "maintenance":
                for equipment in order.equipment_ids:
                    maint_equip = equipment.maintenance_equipment_id
                    if maint_equip:
                        team_id = maint_equip.maintenance_team_id.id
                        self.env["maintenance.request"].with_context(
                            fsm_order=True
                        ).create(
                            {
                                "name": f"{order.name} - {maint_equip.name}",
                                "equipment_id": maint_equip.id,
                                "category_id": maint_equip.category_id.id,
                                "request_date": fields.Date.context_today(order),
                                "maintenance_type": "corrective",
                                "maintenance_team_id": team_id,
                                "schedule_date": order.request_early,
                                "description": order.description,
                                "fsm_order_id": order.id,
                            }
                        )
        return orders
