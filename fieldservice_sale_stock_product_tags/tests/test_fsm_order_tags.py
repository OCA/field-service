# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestFSMOrderTags(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FSMOrder = cls.env["fsm.order"]
        cls.ProductTag = cls.env["product.template.tag"]

        cls.product_10 = cls.env.ref("product.product_product_10")
        cls.product_25 = cls.env.ref("product.product_product_25")
        cls.product_10.write({"field_service_tracking": "sale"})
        cls.product_25.write({"field_service_tracking": "sale"})

        cls.prod_tag1 = cls.ProductTag.create({"name": "Tag A"})
        cls.prod_tag2 = cls.ProductTag.create({"name": "Tag B"})
        cls.product_10.tag_ids |= cls.prod_tag1
        cls.product_25.tag_ids |= cls.prod_tag2

        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.fsm_order = cls.FSMOrder.create({"location_id": cls.test_location.id})

    def _isp_account_installed(self):
        """Checks if the 'fieldservice_isp_account' module is installed."""
        module = self.env["ir.module.module"].search(
            [("name", "=", "fieldservice_isp_account"), ("state", "=", "installed")]
        )
        return bool(module)

    def _fulfill_order(self, order):
        """Prepare FSM order for completion."""
        analytic_account = self.env.ref("analytic.analytic_administratif")
        self.test_location.analytic_account_id = analytic_account.id
        timesheet = self.env["account.analytic.line"].create(
            {
                "name": "timesheet_line",
                "unit_amount": 1,
                "account_id": analytic_account.id,
                "user_id": self.env.ref("base.partner_admin").id,
                "product_id": self.env.ref(
                    "fieldservice_isp_account.field_service_regular_time"
                ).id,
            }
        )
        order.write({"employee_timesheet_ids": [(6, 0, timesheet.ids)]})
        return order

    def test_fsm_order_tags_updated_on_sale_events(self):
        """Test FSM order tags sync on SO confirmation, new line add, and product tag change."""
        SaleOrder = self.env["sale.order"]
        SaleOrderLine = self.env["sale.order.line"]

        sale_order = SaleOrder.create(
            {
                "partner_id": self.test_location.partner_id.id,
                "fsm_location_id": self.test_location.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_10.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_10.uom_id.id,
                            "price_unit": self.product_10.lst_price,
                            "name": self.product_10.name,
                        },
                    )
                ],
            }
        )

        sale_order.action_confirm()

        fsm_orders = self.env["fsm.order"].search([("sale_id", "=", sale_order.id)])
        self.assertTrue(fsm_orders, "FSM order was created upon SO confirmation.")
        fsm_order = fsm_orders[0]

        # Initially only Tag A should be present
        self.assertIn(self.prod_tag1.name, fsm_order.tag_ids.mapped("name"))
        self.assertNotIn(self.prod_tag2.name, fsm_order.tag_ids.mapped("name"))

        # Add a second product to the sale order, which has Tag B
        SaleOrderLine.create(
            {
                "order_id": sale_order.id,
                "product_id": self.product_25.id,
                "product_uom_qty": 1,
                "product_uom": self.product_25.uom_id.id,
                "price_unit": self.product_25.lst_price,
                "name": self.product_25.name,
            }
        )

        sale_order._link_pickings_to_fsm()  # Ensure FSM tag update logic is triggered

        # Now both Tag A and Tag B should be present
        self.assertIn(self.prod_tag1.name, fsm_order.tag_ids.mapped("name"))
        self.assertIn(self.prod_tag2.name, fsm_order.tag_ids.mapped("name"))

        # Update product_10 by adding a new tag
        new_tag = self.ProductTag.create({"name": "Tag C"})
        self.product_10.product_tmpl_id.write({"tag_ids": [(4, new_tag.id)]})

        # Now Tag C should also be present
        self.assertIn(new_tag.name, fsm_order.tag_ids.mapped("name"))

    def test_fsm_order_tags_not_updated_when_closed(self):
        """Test that FSM order tags are not updated if the order is closed."""
        if self._isp_account_installed():
            self.fsm_order = self._fulfill_order(self.fsm_order)

        self.fsm_order.write(
            {
                "date_end": fields.Datetime.now(),
                "resolution": "Work completed",
            }
        )
        self.fsm_order.action_complete()

        # Ensure FSM order is closed
        self.assertTrue(
            self.fsm_order.stage_id.is_closed, "FSM order should be closed."
        )

        # Add new tag to one of the products and write it
        closed_tag = self.ProductTag.create({"name": "Closed Tag"})
        self.product_10.product_tmpl_id.write({"tag_ids": [(4, closed_tag.id)]})

        # Closed FSM order should NOT get updated with this tag
        self.assertNotIn(closed_tag.name, self.fsm_order.tag_ids.mapped("name"))
