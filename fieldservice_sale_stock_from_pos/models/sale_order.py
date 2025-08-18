# Copyright 2025 Bernat Obrador APSL-Nagarro (bobrador@apsl.net).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _link_pickings_to_fsm(self):
        if not any(rec.pos_order_line_ids for rec in self):
            return super()._link_pickings_to_fsm()

        for order in self:
            fsm_order = self.env["fsm.order"].search(
                [
                    ("sale_id", "=", order.id),
                    ("sale_line_id", "=", False),
                ],
                limit=1,
            )

            if order.procurement_group_id:
                order.procurement_group_id.fsm_order_id = fsm_order.id

            pickings = order.pos_order_line_ids[
                0
            ].order_id.picking_ids or order.picking_ids.filtered(
                lambda p: p.state != "cancel"
            )

            for picking in pickings:
                picking.write(order.prepare_fsm_values_for_stock_picking(fsm_order))
                picking.action_confirm()
                # cancel the picking from se SO and unlink it from FSM order
                order.picking_ids[0].action_cancel()
                order.picking_ids[0].fsm_order_id = False
                for move in picking.move_ids:
                    move.write(order.prepare_fsm_values_for_stock_move(fsm_order))
            if fsm_order:
                self._create_activity(fsm_order, order.pos_order_line_ids[0].order_id)

    @api.depends("partner_id", "partner_shipping_id")
    def _compute_fsm_location_id(self):
        res = super()._compute_fsm_location_id()
        for so in self:
            # Create the partner location automatically if it does not exist
            if not so.fsm_location_id and so.partner_id:
                try:
                    if not so.partner_id.fsm_location:
                        self.env["fsm.wizard"].action_convert_location(so.partner_id)
                    so.fsm_location_id = so.partner_id.fsm_location_id
                except Exception:
                    so.fsm_location_id = False
        return res

    @api.model
    def create_order_from_pos(self, order_data, action):
        res = super().create_order_from_pos(order_data, action)
        sale_order = self.browse(res["sale_order_id"])
        fsm_orders = sale_order.mapped("fsm_order_ids")

        if action in ["delivered", "invoiced"] and fsm_orders:
            if not self._is_fieldservice_isp_flow_installed():
                fsm_orders.action_complete()
            else:
                self._process_fsm_orders_with_isp_flow(sale_order, fsm_orders)

        return res

    def _is_fieldservice_isp_flow_installed(self):
        """Check if the 'fieldservice_isp_flow' module is installed."""
        return bool(
            self.env["ir.module.module"]
            .sudo()
            .search_count(
                [("name", "=", "fieldservice_isp_flow"), ("state", "=", "installed")]
            )
        )

    def _process_fsm_orders_with_isp_flow(self, sale_order, fsm_orders):
        """Custom processing for FSM orders when 'fieldservice_isp_flow'
        module is installed."""
        today = fields.Date.context_today(self)
        fs_worker = self.env["fsm.person"].search(
            [("partner_id", "=", self.env.user.partner_id.id)], limit=1
        )
        fs_worker = fs_worker or self.env["fsm.person"].search([], limit=1)
        if not fs_worker:
            raise ValueError(_("No FSM worker found to assign the order."))

        for order in fsm_orders:
            order.person_id = fs_worker.id
            order.action_assign()
            order.scheduled_date_start = today
            order.action_schedule()
            order.date_start = today
            order.date_end = today
            order.resolution = f"Completed From POS:{sale_order.name}"
            order.action_complete()

    def _create_activity(self, fsm_order, pos_order):
        pos_config = self.env["pos.config"].browse(pos_order.config_id.id)
        user = pos_config.fsm_notification_user_id

        if user:
            self.env["mail.activity"].create(
                {
                    "res_model_id": self.env["ir.model"]._get_id("fsm.order"),
                    "res_id": fsm_order.id,
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "summary": _("Review FSM Order"),
                    "note": _("Review and assign this FSM order created from POS."),
                    "user_id": user.id,
                    "date_deadline": fields.Date.context_today(self),
                }
            )
