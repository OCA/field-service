from odoo import fields
from odoo.tests.common import TransactionCase


class TestFSMPartialDeliveryWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.FSMPartialDeliveryWizard = cls.env["fsm.partial.delivery.wizard"]

        cls.partner = cls.env.ref("fieldservice.test_loc_partner")
        cls.product = cls.env.ref("product.product_order_01")
        cls.product.write({"field_service_tracking": "sale"})

        cls.fsm_route_day = cls.env.ref("fieldservice_route.fsm_route_day_0")
        cls.fsm_person = cls.env.ref("fieldservice.test_person")
        cls.route = cls.env["fsm.route"].create(
            {
                "name": "Test Route",
                "fsm_person_id": cls.fsm_person.id,
                "day_ids": [(6, 0, [cls.fsm_route_day.id])],
                "max_order": 1000,
            }
        )

        cls.fsm_location = cls.env.ref("fieldservice.test_location")
        cls.fsm_location.write({"fsm_route_id": cls.route.id})

        cls.sale_order = cls.SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "fsm_location_id": cls.fsm_location.id,
                "order_line": [
                    (0, 0, {"product_id": cls.product.id, "product_uom_qty": 70})
                ],
                "state": "draft",
            }
        )
        cls.sale_order.action_confirm()
        # In Odoo 18, fsm_order_ids is a computed field that may not be
        # immediately populated after action_confirm(); search directly instead.
        cls.fsm_order = cls.env["fsm.order"].search(
            [("sale_id", "=", cls.sale_order.id)], limit=1
        )
        if not cls.fsm_order:
            cls.sale_order._field_service_generation()
            cls.fsm_order = cls.env["fsm.order"].search(
                [("sale_id", "=", cls.sale_order.id)], limit=1
            )
        cls.picking = cls.fsm_order.picking_ids
        # Use warehouse stock location instead of picking.location_id which
        # may be null when the picking hasn't been fully processed yet.
        cls.stock_location = cls.sale_order.warehouse_id.lot_stock_id

        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.stock_location.id,
                "quantity": 50.0,
            }
        )

        cls.env["ir.config_parameter"].set_param(
            "fieldservice_stock.auto_validate_pickings", True
        )

    def _is_isp_account_installed(self):
        module = self.env["ir.module.module"].search(
            [("name", "=", "fieldservice_isp_account")]
        )
        return bool(module and module.state == "installed")

    def _add_timesheet_to_order(self, order):
        analytic_account = self.env["account.analytic.account"].create(
            {"name": "Test Analytic Account"}
        )
        self.fsm_location.analytic_account_id = analytic_account.id
        analytic_product = self.env["product.product"].search(
            [("type", "=", "service")], limit=1
        )
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "timesheet_line",
                "unit_amount": 1,
                "account_id": analytic_account.id,
                "user_id": self.env.ref("base.partner_admin").id,
                "product_id": analytic_product.id,
            }
        )
        order.write(
            {
                "employee_timesheet_ids": [(6, 0, timesheet.ids)],
            }
        )
        return order

    def complete_fsm_order(self, fsm_order):
        if self._is_isp_account_installed():
            self._add_timesheet_to_order(fsm_order)
        fsm_order.write(
            {"date_end": fields.Datetime.now(), "resolution": "Test Resolution"}
        )

    def test_wizard_initialization(self):
        wizard = self.FSMPartialDeliveryWizard.with_context(
            active_id=self.fsm_order.id
        ).create({})
        self.assertEqual(wizard.fsm_order_id, self.fsm_order)
        self.assertEqual(len(wizard.sale_line_ids), 1)
        self.assertEqual(wizard.sale_line_ids[0].product_id, self.product)
        self.assertEqual(wizard.sale_line_ids[0].requested_quantity, 70)
        self.assertEqual(wizard.sale_line_ids[0].quantity_done, 0)

    def test_over_delivery_without_validation_error(self):
        # In Odoo 18, the wizard no longer raises UserError for over-delivery;
        # it simply allows it and updates qty_delivered accordingly.
        wizard = self.FSMPartialDeliveryWizard.with_context(
            active_id=self.fsm_order.id
        ).create({})
        wizard.sale_line_ids[0].quantity_done = 100.0
        self.complete_fsm_order(self.fsm_order)
        wizard.action_confirm_partial_delivery()

        sale_line = self.sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        self.assertEqual(sale_line.qty_delivered, 100.0)

    def test_allow_over_delivery_with_sufficient_stock(self):
        self.env["ir.config_parameter"].set_param(
            "fieldservice_stock.auto_validate_pickings", True
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.stock_location.id,
                "quantity": 100.0,
            }
        )
        wizard = self.FSMPartialDeliveryWizard.with_context(
            active_id=self.fsm_order.id
        ).create({})
        wizard.sale_line_ids[0].quantity_done = 75.0

        self.complete_fsm_order(self.fsm_order)
        wizard.action_confirm_partial_delivery()

        sale_line = self.sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        self.assertEqual(sale_line.qty_delivered, 75.0)
        self.assertEqual(
            self.fsm_order.stage_id.id,
            self.env.ref("fieldservice.fsm_stage_completed").id,
        )

    def test_allow_over_delivery_for_consumables(self):
        self.env["ir.config_parameter"].set_param(
            "fieldservice_stock.auto_validate_pickings", True
        )

        consumable = self.env["product.product"].create(
            {
                "name": "Test Consumable Product",
                "type": "consu",
                "field_service_tracking": "sale",
            }
        )

        sale_order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "fsm_location_id": self.fsm_location.id,
                "order_line": [
                    (0, 0, {"product_id": consumable.id, "product_uom_qty": 70})
                ],
                "state": "draft",
            }
        )
        sale_order.action_confirm()
        fsm_order = self.env["fsm.order"].search(
            [("sale_id", "=", sale_order.id)], limit=1
        )
        if not fsm_order:
            sale_order._field_service_generation()
            fsm_order = self.env["fsm.order"].search(
                [("sale_id", "=", sale_order.id)], limit=1
            )

        wizard = self.FSMPartialDeliveryWizard.with_context(
            active_id=fsm_order.id
        ).create({})
        wizard.sale_line_ids[0].quantity_done = 100.0

        self.complete_fsm_order(fsm_order)
        wizard.action_confirm_partial_delivery()

        sale_line = sale_order.order_line.filtered(
            lambda line: line.product_id == consumable
        )
        self.assertEqual(sale_line.qty_delivered, 100.0)
        self.assertEqual(
            fsm_order.stage_id.id, self.env.ref("fieldservice.fsm_stage_completed").id
        )

    def test_create_backorder_sale_for_undelivered_qty(self):
        wizard = self.FSMPartialDeliveryWizard.with_context(
            active_id=self.fsm_order.id
        ).create({})
        wizard.sale_line_ids[0].quantity_done = 20.0

        self.complete_fsm_order(self.fsm_order)
        self.product.write({"create_backorder_sale": True})
        wizard.action_confirm_partial_delivery()

        sale_line = self.sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        self.assertEqual(sale_line.qty_delivered, 20.0)

        new_sales = self.env["sale.order"].search(
            [("origin", "=", self.sale_order.name), ("id", "!=", self.sale_order.id)]
        )
        self.assertTrue(new_sales)

        new_sale = new_sales[0]
        new_line = new_sale.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        self.assertTrue(new_line)
        self.assertEqual(new_line.product_uom_qty, 50.0)

    def test_full_delivery(self):
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.stock_location.id,
                "quantity": 100.0,
            }
        )
        wizard = self.FSMPartialDeliveryWizard.with_context(
            active_id=self.fsm_order.id
        ).create({})
        wizard.sale_line_ids[0].quantity_done = 70.0

        self.complete_fsm_order(self.fsm_order)
        wizard.action_confirm_partial_delivery()

        sale_line = self.sale_order.order_line.filtered(
            lambda line: line.product_id == self.product
        )
        self.assertEqual(sale_line.qty_delivered, 70.0)
        self.assertEqual(
            self.fsm_order.stage_id.id,
            self.env.ref("fieldservice.fsm_stage_completed").id,
        )

    def test_deliver_new_product(self):
        new_product = self.env["product.product"].create(
            {
                "name": "New Product",
                "type": "consu",
                "is_storable": True,
                "field_service_tracking": "sale",
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": new_product.id,
                "location_id": self.stock_location.id,
                "quantity": 100.0,
            }
        )
        wizard = self.FSMPartialDeliveryWizard.with_context(
            active_id=self.fsm_order.id
        ).create({})

        self.env["fsm.partial.delivery.line"].create(
            {
                "wizard_id": wizard.id,
                "product_id": new_product.id,
                "requested_quantity": 0.0,
                "quantity_done": 5.0,
            }
        )

        self.complete_fsm_order(self.fsm_order)
        wizard.action_confirm_partial_delivery()

        sale_line = self.sale_order.order_line.filtered(
            lambda line: line.product_id == new_product
        )
        self.assertTrue(sale_line)
        self.assertEqual(sale_line.product_uom_qty, 5.0)
        self.assertEqual(
            self.fsm_order.stage_id.id,
            self.env.ref("fieldservice.fsm_stage_completed").id,
        )
