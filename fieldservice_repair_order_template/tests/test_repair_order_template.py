# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests import Form, TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestRepairOrderTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.env.user.groups_id += cls.env.ref("fieldservice.group_fsm_template")
        cls.repair_template = cls.env.ref(
            "repair_order_template.repair_order_template_demo"
        )
        cls.template = cls.env["fsm.template"].create(
            {
                "name": "Test Template",
                "type_id": cls.env.ref("fieldservice_repair.fsm_order_type_repair").id,
                "repair_order_template_id": cls.repair_template.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Product A", "type": "product"}
        )
        cls.lot = cls.env["stock.lot"].create(
            {
                "name": "sn11",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product.id,
                "inventory_quantity": 10,
                "lot_id": cls.lot.id,
                "location_id": cls.stock_location.id,
            }
        ).action_apply_inventory()
        cls.equipment = cls.env["fsm.equipment"].create(
            {
                "name": "test equipment",
                "product_id": cls.product.id,
                "lot_id": cls.lot.id,
                "current_stock_location_id": cls.env.ref(
                    "stock.stock_location_stock"
                ).id,
            }
        )
        cls.order_vals = {
            "type": cls.env.ref("fieldservice_repair.fsm_order_type_repair").id,
            "location_id": cls.env.ref("fieldservice.test_location").id,
            "equipment_id": cls.equipment.id,
            "date_start": fields.Datetime.today(),
            "date_end": fields.Datetime.today() + timedelta(hours=1),
            "request_early": fields.Datetime.today(),
        }

    def test_repair_order_template_on_create(self):
        order = self.env["fsm.order"].create(
            dict(self.order_vals, template_id=self.template.id)
        )
        self.assertEqual(order.repair_id.repair_order_template_id, self.repair_template)
        self.assertEqual(len(order.repair_id.move_ids), 2)

    def test_repair_order_template_on_write(self):
        order = self.env["fsm.order"].create(self.order_vals)
        with Form(order) as order_form:
            order_form.template_id = self.template
        self.assertEqual(order.repair_id.repair_order_template_id, self.repair_template)
        self.assertEqual(len(order.repair_id.move_ids), 2)

    def test_repair_order_template_with_onchange_template_flow(self):
        """Test the flow when the type is inferred from the template

        This case is the one implemented in fieldservice_recurring. In the future,
        the onchange should move to a computed method and this should not be required
        anymore.
        """
        order_vals = self.order_vals.copy()
        order_vals.pop("type", None)
        order = self.env["fsm.order"].create(
            dict(order_vals, template_id=self.template.id)
        )
        order._onchange_template_id()
        self.assertEqual(
            order.type, self.env.ref("fieldservice_repair.fsm_order_type_repair")
        )
        self.assertEqual(order.repair_id.repair_order_template_id, self.repair_template)
        self.assertEqual(len(order.repair_id.move_ids), 2)
