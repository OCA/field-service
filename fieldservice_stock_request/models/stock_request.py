# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockRequest(models.Model):
    _inherit = "stock.request"

    fsm_order_id = fields.Many2one(
        "fsm.order", string="FSM Order", ondelete="cascade", index=True, copy=False
    )

    def _update_stock_request_order_data(self):
        if self.order_id and self.direction and self.state == "draft":
            picking_type_id = self.env["stock.picking.type"].search(
                [
                    ("code", "=", "stock_request_order"),
                    ("warehouse_id", "=", self.warehouse_id.id),
                ],
                limit=1,
            )
            order = self.env["stock.request.order"].search(
                [
                    ("fsm_order_id", "=", self.fsm_order_id.id),
                    ("warehouse_id", "=", self.warehouse_id.id),
                    ("picking_type_id", "=", picking_type_id.id),
                    ("direction", "=", self.direction),
                    ("state", "=", "draft"),
                ],
                order="id asc",
            )
            self.order_id = order.id

    @api.onchange("direction", "fsm_order_id")
    def _onchange_location_id(self):
        super()._onchange_location_id()
        if self.fsm_order_id:
            if self.direction == "outbound":
                # Inventory location of the FSM location of the order
                self.location_id = (
                    self.fsm_order_id.location_id.inventory_location_id.id
                )
            else:
                self.location_id = self.fsm_order_id.warehouse_id.lot_stock_id.id
            self._update_stock_request_order_data()

    def prepare_stock_request_order_values(self):
        res = {
            "expected_date": self.expected_date,
            "picking_policy": self.picking_policy,
            "warehouse_id": self.warehouse_id.id,
            "direction": self.direction,
            "location_id": self.location_id.id,
        }
        return res

    def prepare_order_values(self, vals):
        res = {
            "expected_date": vals["expected_date"],
            "picking_policy": vals["picking_policy"],
            "warehouse_id": vals["warehouse_id"],
            "direction": vals["direction"],
            "location_id": vals["location_id"],
        }
        if "fsm_order_id" in vals and vals["fsm_order_id"]:
            res.update({"fsm_order_id": vals["fsm_order_id"]})
        return res

    @api.model
    def create(self, vals):
        if "fsm_order_id" in vals and vals["fsm_order_id"]:
            fsm_order = self.env["fsm.order"].browse(vals["fsm_order_id"])
            fsm_order.request_stage = "draft"
            vals["warehouse_id"] = fsm_order.warehouse_id.id
            picking_type_id = self.env["stock.picking.type"].search(
                [
                    ("code", "=", "stock_request_order"),
                    ("warehouse_id", "=", vals["warehouse_id"]),
                ],
                limit=1,
            )
            if not picking_type_id:
                raise UserError(
                    _(
                        "There is no any inventory Operations Type:"
                        "stock_request_order record for %s Warehouse."
                    )
                    % fsm_order.warehouse_id.display_name
                )
            order = self.env["stock.request.order"].search(
                [
                    ("fsm_order_id", "=", vals["fsm_order_id"]),
                    ("warehouse_id", "=", vals["warehouse_id"]),
                    ("picking_type_id", "=", picking_type_id.id),
                    ("direction", "=", vals["direction"]),
                    ("state", "=", "draft"),
                ],
                order="id asc",
            )

            # User created a new SRO Manually
            if len(order) > 1:
                raise UserError(
                    _(
                        "There is already a Stock Request Order \
                                  with the same Field Service Order and \
                                  Warehouse that is in Draft state. Please \
                                  add this Stock Request there. \
                                  (%s)"
                    )
                    % order[0].name
                )
            # Made from an FSO for the first time, create the SRO here
            elif not order and vals.get("fsm_order_id"):
                values = self.prepare_order_values(vals)
                values.update(
                    {
                        "picking_type_id": picking_type_id.id,
                        "warehouse_id": vals["warehouse_id"],
                    }
                )
                if values["direction"] == "inbound":
                    values.update(
                        {
                            "location_id": self.env["stock.warehouse"]
                            .browse(vals["warehouse_id"])
                            .lot_stock_id.id
                        }
                    )
                vals["order_id"] = self.env["stock.request.order"].create(values).id
            # There is an SRO made from FSO, assign here
            elif len(order) == 1 and vals.get("fsm_order_id"):
                vals["expected_date"] = order.expected_date
                vals["order_id"] = order.id
        return super().create(vals)

    def write(self, vals):
        for stock_req in self:
            if "direction" in vals or "expected_date" in vals:
                direction = vals.get("direction")
                if "direction" not in vals:
                    direction = stock_req.direction
                picking_type_id = self.env["stock.picking.type"].search(
                    [
                        ("code", "=", "stock_request_order"),
                        ("warehouse_id", "=", stock_req.warehouse_id.id),
                    ],
                    limit=1,
                )
                if stock_req.fsm_order_id:
                    order = self.env["stock.request.order"].search(
                        [
                            ("fsm_order_id", "=", stock_req.fsm_order_id.id),
                            ("warehouse_id", "=", stock_req.warehouse_id.id),
                            ("picking_type_id", "=", picking_type_id.id),
                            ("direction", "=", direction),
                            ("state", "=", "draft"),
                        ],
                        order="id asc",
                    )
                else:
                    order = stock_req.order_id

                order = self.env["stock.request.order"].search(
                    [
                        ("fsm_order_id", "=", stock_req.fsm_order_id.id),
                        ("warehouse_id", "=", stock_req.warehouse_id.id),
                        ("picking_type_id", "=", picking_type_id.id),
                        ("direction", "=", direction),
                        ("state", "=", "draft"),
                    ],
                    order="id asc",
                )
                # User created a new SRO Manually
                if len(order) > 1:
                    raise UserError(
                        _(
                            "There is already a Stock Request Order \
                                      with the same Field Service Order and \
                                      Warehouse that is in Draft state. Please \
                                      add this Stock Request there. \
                                      (%s)"
                        )
                        % order[0].name
                    )
                # FSO: Update Values into it.
                elif order:
                    values = stock_req.prepare_stock_request_order_values()
                    values.update(
                        {
                            "direction": vals.get("direction") or stock_req.direction,
                            "location_id": vals.get("location_id")
                            or stock_req.location_id.id,
                            "expected_date": vals.get("expected_date")
                            or stock_req.expected_date,
                        }
                    )
                    order.write(values)
                    vals["order_id"] = order.id
                # Create SRO If not found then.
                elif not order:
                    values = stock_req.prepare_stock_request_order_values()
                    if vals.get("direction", False) and vals.get("location_id", False):
                        values.update(
                            {
                                "direction": vals.get("direction")
                                or stock_req.direction,
                                "location_id": vals.get("location_id")
                                or stock_req.location_id.id,
                                "expected_date": vals.get("expected_date")
                                or stock_req.expected_date,
                            }
                        )
                    elif vals.get("expected_date", False):
                        values.update(
                            {
                                "expected_date": vals.get("expected_date")
                                or stock_req.expected_date,
                            }
                        )

                    vals["order_id"] = self.env["stock.request.order"].create(values).id

        return super().write(vals)

    def _prepare_procurement_values(self, group_id=False):
        res = super()._prepare_procurement_values(group_id=group_id)
        if self.fsm_order_id:
            res.update(
                {
                    "fsm_order_id": self.fsm_order_id.id,
                    "partner_id": self.fsm_order_id.location_id.shipping_address_id.id
                    or self.fsm_order_id.location_id.partner_id.id,
                }
            )
        return res

    def _prepare_procurement_group_values(self):
        if self.fsm_order_id:
            return {
                "name": self.fsm_order_id.display_name,
                "fsm_order_id": self.fsm_order_id.id,
                "move_type": "direct",
            }
        return {}

    def _action_confirm(self):
        for req in self:
            if (not req.procurement_group_id) and req.fsm_order_id:
                group = self.env["procurement.group"].search(
                    [("fsm_order_id", "=", req.fsm_order_id.id)]
                )
                if not group:
                    values = req._prepare_procurement_group_values()
                    group = req.env["procurement.group"].create(values)
                if req.order_id:
                    req.order_id.procurement_group_id = group.id
                req.procurement_group_id = group.id
                res = super(StockRequest, req)._action_confirm()
                req.fsm_order_id.request_stage = "open"
            else:
                res = super(StockRequest, req)._action_confirm()
        return res
