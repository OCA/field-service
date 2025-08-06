# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestFSMRepairCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.stock_location = cls.env.ref("stock.stock_location_customers")
        cls.repair_type = cls.env.ref("fieldservice_repair.fsm_order_type_repair")
        cls.fsm_type = cls.env["fsm.order.type"].create(
            {"name": "FSM", "internal_type": "fsm"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
            }
        )
        cls.lot = cls.env["stock.lot"].create(
            {
                "name": "sn11",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.equipment = cls.env["fsm.equipment"].create(
            {
                "name": "test equipment",
                "product_id": cls.product.id,
                "lot_id": cls.lot.id,
            }
        )
        # Create some stocks so that the current stock location is properly computed
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.stock_location.id,
                "lot_id": cls.lot.id,
                "quantity": 100,
            }
        )

    def _prepare_fsm_order_vals(self):
        return {
            "type": self.repair_type.id,
            "location_id": self.test_location.id,
            "date_start": fields.Datetime.today(),
            "date_end": fields.Datetime.today() + timedelta(hours=100),
            "request_early": fields.Datetime.today(),
            "equipment_id": self.equipment.id,
        }

    def test_fsm_repair_order_fails_if_no_equipment(self):
        with self.assertRaisesRegex(
            ValidationError,
            "The Equipment must be set to create a Repair Order.",
        ):
            order_vals = self._prepare_fsm_order_vals()
            order_vals.pop("equipment_id")
            self.env["fsm.order"].create(order_vals)

    def test_fsm_repair_order_fails_if_no_current_stock_location(self):
        self.env["stock.quant"].search([("product_id", "=", self.product.id)]).unlink()
        self.equipment.invalidate_recordset(["current_stock_location_id"])
        with self.assertRaisesRegex(
            ValidationError,
            r"Cannot create the Repair Order because the Equipment '.*' "
            r"does not have a Current Inventory Location set.",
        ):
            self.env["fsm.order"].create(self._prepare_fsm_order_vals())

    def test_fsm_repair_order_creates_repair_order(self):
        order = self.env["fsm.order"].create(self._prepare_fsm_order_vals())
        self.assertTrue(order.repair_id, "Repair order was created")
        self.assertEqual(order.repair_id.state, "draft")
        self.assertEqual(order.repair_id.name, order.name)
        self.assertEqual(order.repair_id.product_id, self.equipment.product_id)
        self.assertEqual(order.repair_id.product_uom, self.equipment.product_id.uom_id)
        self.assertEqual(order.repair_id.location_id, self.stock_location)
        self.assertEqual(order.repair_id.lot_id, self.equipment.lot_id)
        self.assertEqual(order.repair_id.product_qty, 1)
        self.assertEqual(order.repair_id.internal_notes, order.description)

    def test_fsm_repair_order_is_created_when_type_is_switched_to_repair(self):
        order_vals = self._prepare_fsm_order_vals()
        order_vals["type"] = self.fsm_type.id
        order = self.env["fsm.order"].create(order_vals)
        self.assertFalse(order.repair_id, "Repair order was not created, wrong type")
        order.type = self.repair_type
        self.assertTrue(order.repair_id, "Repair order was created")

    def test_fsm_repair_order_is_canceled_when_type_is_switched_to_not_repair(self):
        order_vals = self._prepare_fsm_order_vals()
        order = self.env["fsm.order"].create(order_vals)
        self.assertTrue(order.repair_id, "Repair order was created")
        self.assertEqual(order.repair_id.state, "draft")
        repair_order = order.repair_id
        order.type = self.fsm_type
        self.assertEqual(repair_order.state, "cancel", "Repair order was canceled")
        self.assertFalse(order.repair_id, "Repair order was unlinked from the FSM")

    def test_warning_is_shown_when_type_is_switched_to_not_repair(self):
        order_vals = self._prepare_fsm_order_vals()
        order = self.env["fsm.order"].create(order_vals)
        with Form(order) as form:
            with self.assertLogs("odoo.tests.form.onchange") as log_catcher:
                form.type = self.fsm_type
                self.assertIn(
                    "The repair order will be cancelled",
                    log_catcher.output[0],
                )
            with self.assertNoLogs("odoo.tests.form.onchange"):
                form.type = self.repair_type
