from odoo.tests.common import TransactionCase


class TestFsmCreateSoWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.days = [
            cls.env.ref("fieldservice_route.fsm_route_day_0").id,
            cls.env.ref("fieldservice_route.fsm_route_day_1").id,
            cls.env.ref("fieldservice_route.fsm_route_day_2").id,
            cls.env.ref("fieldservice_route.fsm_route_day_3").id,
            cls.env.ref("fieldservice_route.fsm_route_day_4").id,
            cls.env.ref("fieldservice_route.fsm_route_day_5").id,
            cls.env.ref("fieldservice_route.fsm_route_day_6").id,
        ]

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "Test Worker",
            }
        )

        cls.fsm_person = cls.env["fsm.person"].create(
            {
                "name": "Test FSM Person",
                "partner_id": cls.partner_2.id,
            }
        )

        fsm_route = cls.env["fsm.route"].create(
            {
                "name": "Test Route",
                "max_order": 100,
                "fsm_person_id": cls.fsm_person.id,
                "day_ids": [(6, 0, cls.days)],
            }
        )

        location_vals = {
            "name": "Test Location",
            "partner_id": cls.partner.id,
            "owner_id": cls.partner.id,
            "fsm_route_id": fsm_route.id,
        }
        if cls.env["ir.module.module"].search(
            [
                ("name", "=", "fieldservice_account_analytic"),
                ("state", "=", "installed"),
            ]
        ):
            location_vals["customer_id"] = cls.partner.id

        cls.location = cls.env["fsm.location"].create(location_vals)

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "field_service_tracking": "sale",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "lst_price": 100.0,
            }
        )

    def test_create_sale_order_from_wizard(self):
        wizard = self.env["fsm.create.so.wizard"].create(
            {
                "location_id": self.location.id,
            }
        )

        self.env["fsm.create.so.wizard.line"].create(
            {
                "wizard_id": wizard.id,
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "quantity": 2.0,
                "discount": 10.0,
            }
        )

        action = wizard.action_create_sale_order()

        self.assertEqual(action["res_model"], "fsm.order")

        sale_order = self.env["sale.order"].search(
            [("partner_id", "=", self.partner.id)], limit=1
        )

        self.assertTrue(sale_order)
        self.assertEqual(len(sale_order.order_line), 1)
        self.assertEqual(sale_order.order_line.product_id, self.product)
        self.assertEqual(sale_order.order_line.product_uom_qty, 2.0)
        self.assertEqual(sale_order.order_line.discount, 10.0)

        self.assertTrue(sale_order.fsm_order_ids)
