# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import Command, fields
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
        cls.equipment_1 = cls.env["fsm.equipment"].create(
            {
                "name": "Equipment 1",
                "product_id": cls.product.id,
                "lot_id": cls.lot.id,
            }
        )
        cls.equipment_2 = cls.env["fsm.equipment"].create(
            {
                "name": "Equipment 2",
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

    def _prepare_fsm_order_vals(self, equipments):
        return {
            "type": self.repair_type.id,
            "location_id": self.test_location.id,
            "date_start": fields.Datetime.today(),
            "date_end": fields.Datetime.today() + timedelta(hours=100),
            "request_early": fields.Datetime.today(),
            "equipment_ids": [Command.link(eq.id) for eq in equipments],
        }

    def test_fsm_repair_order_fails_if_no_equipment(self):
        with self.assertRaisesRegex(
            ValidationError,
            "Equipments must be set to create Repair Orders.",
        ):
            order_vals = self._prepare_fsm_order_vals(self.equipment_1)
            order_vals.pop("equipment_ids")
            self.env["fsm.order"].create(order_vals)

    def test_fsm_repair_order_fails_if_no_current_stock_location(self):
        self.env["stock.quant"].search([("product_id", "=", self.product.id)]).unlink()
        self.equipment_1.invalidate_recordset(["current_stock_location_id"])
        with self.assertRaisesRegex(
            ValidationError,
            r"Cannot create the Repair Order because the Equipment '.*' "
            r"does not have a Current Inventory Location set.",
        ):
            self.env["fsm.order"].create(self._prepare_fsm_order_vals(self.equipment_1))

    def test_fsm_repair_order_creates_repair_order(self):
        order = self.env["fsm.order"].create(
            self._prepare_fsm_order_vals(self.equipment_1)
        )
        self.assertTrue(order.repair_ids, "Repair order was created")
        repair_order = order.repair_ids[0]
        self.assertEqual(repair_order.state, "draft")
        self.assertEqual(repair_order.name, f"{order.name} - {self.equipment_1.name}")
        self.assertEqual(repair_order.product_id, self.equipment_1.product_id)
        self.assertEqual(repair_order.product_uom, self.equipment_1.product_id.uom_id)
        self.assertEqual(repair_order.location_id, self.stock_location)
        self.assertEqual(repair_order.lot_id, self.equipment_1.lot_id)
        self.assertEqual(repair_order.product_qty, 1)
        self.assertEqual(repair_order.internal_notes, order.description)

    def test_fsm_repair_order_is_created_when_type_is_switched_to_repair(self):
        order_vals = self._prepare_fsm_order_vals(self.equipment_1)
        order_vals["type"] = self.fsm_type.id
        order = self.env["fsm.order"].create(order_vals)
        self.assertFalse(order.repair_ids, "Repair order was not created, wrong type")
        order.type = self.repair_type
        self.assertTrue(order.repair_ids, "Repair order was created")

    def test_fsm_repair_order_is_canceled_when_type_is_switched_to_not_repair(self):
        order_vals = self._prepare_fsm_order_vals(self.equipment_1)
        order = self.env["fsm.order"].create(order_vals)
        self.assertTrue(order.repair_ids, "Repair order was created")
        repair_order = order.repair_ids[0]
        self.assertEqual(repair_order.state, "draft")
        order.type = self.fsm_type
        self.assertEqual(repair_order.state, "cancel", "Repair order was canceled")
        self.assertFalse(order.repair_ids, "Repair order was unlinked from the FSM")

    def test_warning_is_shown_when_type_is_switched_to_not_repair(self):
        order_vals = self._prepare_fsm_order_vals(self.equipment_1)
        order = self.env["fsm.order"].create(order_vals)
        with Form(order) as form:
            with self.assertLogs("odoo.tests.form.onchange") as log_catcher:
                form.type = self.fsm_type
                self.assertIn(
                    "The repair orders will be cancelled",
                    log_catcher.output[0],
                )
            with self.assertNoLogs("odoo.tests.form.onchange"):
                form.type = self.repair_type

    def test_fsm_repair_order_creates_multiple_repairs_for_multiple_equipments(self):
        order = self.env["fsm.order"].create(
            self._prepare_fsm_order_vals([self.equipment_1, self.equipment_2])
        )
        self.assertEqual(
            len(order.repair_ids), 2, "Two repair orders should be created"
        )

        repair_names = order.repair_ids.mapped("name")
        self.assertIn(f"{order.name} - {self.equipment_1.name}", repair_names)
        self.assertIn(f"{order.name} - {self.equipment_2.name}", repair_names)

        for repair in order.repair_ids:
            self.assertEqual(repair.state, "draft", "Repairs must be in draft")
            self.assertIn(
                repair.lot_id, [self.equipment_1.lot_id, self.equipment_2.lot_id]
            )
            self.assertEqual(repair.product_qty, 1)

    def test_cancel_all_repairs_when_switching_type_with_multiple_equipments(self):
        order = self.env["fsm.order"].create(
            self._prepare_fsm_order_vals([self.equipment_1, self.equipment_2])
        )
        self.assertEqual(len(order.repair_ids), 2)
        order.type = self.fsm_type
        for repair in order.repair_ids:
            self.assertEqual(repair.state, "cancel")
        self.assertFalse(
            order.repair_ids, "All repairs should be unlinked after cancel"
        )

    def test_action_view_repairs_single(self):
        order = self.env["fsm.order"].create(
            self._prepare_fsm_order_vals(self.equipment_1)
        )
        self.assertEqual(len(order.repair_ids), 1, "One repair should be created")

        action = order.action_view_repairs()
        self.assertIsInstance(action, dict, "Action must be a dictionary")
        self.assertEqual(action["res_model"], "repair.order")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["res_id"], order.repair_ids.id)

    def test_action_view_repairs_multiple(self):
        order = self.env["fsm.order"].create(
            self._prepare_fsm_order_vals([self.equipment_1, self.equipment_2])
        )
        self.assertEqual(len(order.repair_ids), 2, "Two repairs should be created")

        action = order.action_view_repairs()
        self.assertIsInstance(action, dict)
        self.assertEqual(action["res_model"], "repair.order")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertIn("list", action["view_mode"])
        self.assertIn("form", action["view_mode"])
        self.assertIn("domain", action)
        self.assertIn(("id", "in", order.repair_ids.ids), [tuple(action["domain"][0])])

    def test_action_view_repairs_none(self):
        order = self.env["fsm.order"].create(
            self._prepare_fsm_order_vals(self.equipment_1)
        )
        order.repair_ids.unlink()
        self.assertFalse(order.repair_ids)

        action = order.action_view_repairs()
        self.assertIsNone(
            action, "No action should be returned when there are no repairs"
        )

    def test_create_repair_orders_no_context_propagation(self):
        # Create an FSM order with a default_priority in context
        # The '2' is a valid value for the fsm.order, but not for the repair.order.
        order = (
            self.env["fsm.order"]
            .with_context(default_priority="2")
            .create(self._prepare_fsm_order_vals(self.equipment_1))
        )
        self.assertEqual(order.repair_ids.priority, "0")
