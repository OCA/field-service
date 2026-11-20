# Copyright (C) 2022 Rafnix Guzman
# Copyright (C) 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FsmEquipmentLocationHistory(models.Model):
    _name = "fsm.equipment.location.history"
    _description = "Equipment Stock Location History"
    _order = "date desc, id desc"

    from_location_id = fields.Many2one(
        "stock.location", string="From Location", required=True
    )
    to_location_id = fields.Many2one(
        "stock.location", string="To Location", required=True
    )
    equipment_id = fields.Many2one("fsm.equipment", string="Equipment", required=True)
    date = fields.Datetime(required=True, default=fields.Datetime.now)
    type_selection = fields.Selection(
        [("inbound", "Inbound"), ("outbound", "Outbound")],
        string="Type",
        required=True,
        default="inbound",
    )
    picking_id = fields.Many2one(
        "stock.picking", string="Transfer", readonly=True, copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        histories = super().create(vals_list)
        for history in histories:
            history._execute_transfer()
        return histories

    def _execute_transfer(self):
        """Move the equipment's serial to the target location with a real
        internal transfer, so quants and traceability stay consistent.

        FSM users have no stock rights, so the transfer runs as superuser once
        the history record was created and its locations read with the user's
        own rights (multi-company rules apply there)."""
        self.ensure_one()
        equipment = self.equipment_id
        if not equipment.lot_id or not equipment.product_id:
            raise UserError(
                _(
                    "Equipment %s has no product/serial number: "
                    "a stock transfer cannot be created."
                )
                % equipment.display_name
            )
        company = (
            self.from_location_id.company_id
            or self.to_location_id.company_id
            or self.env.company
        )
        history = self.sudo().with_company(company)
        picking_type = history._get_transfer_picking_type(company)
        quant = history._get_available_serial_quant()
        picking = history.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "location_id": history.from_location_id.id,
                "location_dest_id": history.to_location_id.id,
                "scheduled_date": history.date,
                "company_id": company.id,
            }
        )
        move = history.env["stock.move"].create(
            {
                "name": equipment.display_name,
                "product_id": equipment.product_id.id,
                "product_uom": equipment.product_id.uom_id.id,
                "product_uom_qty": 1.0,
                "location_id": history.from_location_id.id,
                "location_dest_id": history.to_location_id.id,
                "picking_id": picking.id,
                "date": history.date,
                "company_id": company.id,
            }
        )
        picking.action_confirm()
        # Reserve the equipment's own serial: the generic reservation done on
        # confirmation could pick another serial of the same product.
        picking.do_unreserve()
        history.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "picking_id": picking.id,
                "product_id": equipment.product_id.id,
                "lot_id": equipment.lot_id.id,
                "location_id": quant.location_id.id,
                "location_dest_id": history.to_location_id.id,
                "quantity": 1.0,
            }
        )
        move.picked = True
        picking.button_validate()
        history.picking_id = picking.id
        history._update_equipment_fsm_location()

    def _get_transfer_picking_type(self, company):
        """Internal operation type of the company, preferring the warehouse
        of the source location."""
        picking_types = self.env["stock.picking.type"].search(
            [("code", "=", "internal"), ("company_id", "=", company.id)]
        )
        if not picking_types:
            raise UserError(
                _(
                    "No internal transfer operation type found for company %s. "
                    "Enable Storage Locations in Inventory settings."
                )
                % company.display_name
            )
        warehouse = self.from_location_id.warehouse_id
        return (
            picking_types.filtered(lambda t: t.warehouse_id == warehouse)[:1]
            or picking_types[:1]
        )

    def _get_available_serial_quant(self):
        """Quant of the equipment's serial in the source location that is not
        reserved by another operation."""
        equipment = self.equipment_id
        quants = self.env["stock.quant"].search(
            [
                ("product_id", "=", equipment.product_id.id),
                ("lot_id", "=", equipment.lot_id.id),
                ("location_id", "child_of", self.from_location_id.id),
                ("quantity", ">", 0),
            ]
        )
        quant = quants.filtered(lambda q: q.quantity - q.reserved_quantity >= 1)[:1]
        if not quant:
            raise UserError(
                _(
                    "Serial number %(lot)s is not available in %(location)s "
                    "(missing or reserved by another operation)."
                )
                % {
                    "lot": equipment.lot_id.display_name,
                    "location": self.from_location_id.display_name,
                }
            )
        return quant

    def _update_equipment_fsm_location(self):
        """Point the equipment to the FSM location matching the target stock
        location, when one exists (by inventory location, then by name)."""
        self.ensure_one()
        fsm_location = self.env["fsm.location"].search(
            [("inventory_location_id", "=", self.to_location_id.id)], limit=1
        ) or self.env["fsm.location"].search(
            [("name", "=", self.to_location_id.name)], limit=1
        )
        if fsm_location:
            self.equipment_id.location_id = fsm_location.id
