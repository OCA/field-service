from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFSMStockActionComplete(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FSMOrder = cls.env["fsm.order"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.StockMove = cls.env["stock.move"]
        cls.Product = cls.env["product.product"].search([], limit=1)
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

        cls.fsm_order = cls.FSMOrder.create(
            {
                "location_id": cls.env.ref("fieldservice.test_location").id,
                "date_start": fields.Datetime.now(),
                "date_end": fields.Datetime.now(),
                "request_early": fields.Datetime.now(),
                "resolution": "Test resolution",
            }
        )

        cls.picking = cls.StockPicking.create(
            {
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_out.id,
                "fsm_order_id": cls.fsm_order.id,
            }
        )

        cls.stock_move = cls.StockMove.create(
            {
                "name": "Move Test Product",
                "product_id": cls.Product.id,
                "product_uom_qty": 5.0,
                "product_uom": cls.Product.uom_id.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "picking_id": cls.picking.id,
                "state": "confirmed",
            }
        )

    def test_action_complete_auto_validate_disabled(self):
        """Ensure pickings are not validated when auto_validate_pickings is False."""
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice_stock.auto_validate_pickings", False
        )
        self.stock_move.quantity_done = self.stock_move.product_uom_qty
        self.fsm_order.action_complete()
        self.assertNotEqual(
            self.picking.state,
            "done",
            "Picking should not validate when auto-validate is False.",
        )

    def test_action_complete_validates_pickings(self):
        """Ensure pickings are validated when auto_validate_pickings is True."""
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice_stock.auto_validate_pickings", True
        )
        self.stock_move.quantity_done = self.stock_move.product_uom_qty
        self.fsm_order.action_complete()
        self.assertEqual(
            self.picking.state, "done", "Picking should be validated and set to 'done'."
        )

    def test_action_complete_raises_error_on_insufficient_stock(self):
        """Ensure ValidationError is raised when stock is insufficient."""
        self.env["ir.config_parameter"].sudo().set_param(
            "fieldservice_stock.auto_validate_pickings", True
        )
        product_no_stock = self.env.ref("product.product_product_16_product_template")
        self.StockMove.create(
            {
                "name": "Move Test Product - Waiting",
                "product_id": product_no_stock.id,
                "product_uom_qty": 5.0,
                "product_uom": product_no_stock.uom_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_id": self.picking.id,
                "state": "confirmed",
            }
        )

        self.picking.action_confirm()
        with self.assertRaises(ValidationError):
            self.fsm_order.action_complete()
