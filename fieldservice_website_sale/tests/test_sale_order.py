from odoo.tests.common import TransactionCase


class TestSaleOrderOnchange(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.demo_user = cls.env.ref("base.demo_user0")
        cls.test_person = cls.env.ref("fieldservice.test_person")
        cls.day_monday = cls.env.ref("fieldservice_route.fsm_route_day_0")
        cls.day_wednesday = cls.env.ref("fieldservice_route.fsm_route_day_2")
        cls.test_route = cls.env["fsm.route"].create(
            {
                "name": "Test Route",
                "fsm_person_id": cls.test_person.id,
                "day_ids": [cls.day_monday.id, cls.day_wednesday.id],
                "max_order": 100,
            }
        )

        cls.partner_demo = cls.demo_user.partner_id
        fsm_wizard = cls.env["fsm.wizard"].create({})
        fsm_wizard.with_context(active_ids=[cls.partner_demo.id])
        fsm_wizard.action_convert_location(cls.partner_demo)

        cls.test_location = cls.env["fsm.location"].search(
            [("partner_id", "=", cls.partner_demo.id)]
        )

        cls.test_location.write({"fsm_route_id": cls.test_route.id})
        cls.sale_order = cls.env.ref("sale.portal_sale_order_1")

    def test_onchange_partner_shipping_id(self):
        no_fsm_partner_shipping = self.env["res.partner"].create(
            {"name": "No FSM Shipping Partner", "email": "no_fsm@example.com"}
        )
        self.sale_order.partner_id = no_fsm_partner_shipping.id
        self.sale_order.onchange_partner_id()
        self.sale_order.onchange_partner_shipping_id()

        self.assertFalse(
            self.sale_order.fsm_location_id,
            "The fsm_location_id should be cleared when partner_shipping_id "
            "has no FSM location.",
        )

        self.sale_order.partner_id = self.partner_demo.id
        self.sale_order.onchange_partner_id()
        self.sale_order.onchange_partner_shipping_id()

        self.assertEqual(
            self.sale_order.fsm_location_id.id,
            self.test_location.id,
            "The fsm_location_id should be updated to match the FSM location "
            "of partner_shipping_id.",
        )
