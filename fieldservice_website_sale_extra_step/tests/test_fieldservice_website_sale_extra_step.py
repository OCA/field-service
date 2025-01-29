# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFieldServiceWebsiteSaleExtraStep(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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

        cls.partner = cls.env.ref("base.partner_demo_portal")
        fsm_wizard = cls.env["fsm.wizard"].create({})
        fsm_wizard.with_context(active_ids=[cls.partner.id])
        fsm_wizard.action_convert_location(cls.partner)

        cls.test_location = cls.env["fsm.location"].search(
            [("partner_id", "=", cls.partner.id)]
        )

        cls.test_location.write({"fsm_route_id": cls.test_route.id})

        cls.sale_order = cls.env.ref("sale.portal_sale_order_1")
        cls.sale_order.write({"fsm_location_id": cls.test_location.id})
        cls.sale_order.order_line[0].product_id.write(
            {"field_service_tracking": "sale"}
        )

    def get_active_fsm_order(self):
        """Helper method to retrieve the active FSM order linked to the sale order."""
        return self.env["fsm.order"].search(
            [
                ("sale_id", "=", self.sale_order.id),
                ("sale_line_id", "=", False),
                ("is_closed", "=", False),
            ]
        )

    def test_client_order_ref_propagation(self):
        """Ensure client_order_ref is propagated to FSM order description."""
        self.sale_order.client_order_ref = "Test Reference"
        self.sale_order.action_confirm()
        self.assertEqual(self.get_active_fsm_order().description, "Test Reference")

    def test_customer_message_propagation(self):
        """Ensure customer messages are transferred to FSM order."""
        self.env["mail.message"].create(
            {
                "body": "Customer message during checkout.",
                "model": "sale.order",
                "res_id": self.sale_order.id,
                "message_type": "comment",
            }
        )
        self.sale_order.action_confirm()
        messages = self.get_active_fsm_order().message_ids.filtered(
            lambda m: m.message_type == "comment" and not m.subtype_id
        )
        self.assertTrue(messages)
        self.assertIn("Customer message during checkout.", messages[0].body)

    def test_attachment_propagation(self):
        """Ensure attachments from sale order are copied to FSM order."""
        file = self.env.ref("account.1_ir_attachment_in_invoice_1")
        test_user = self.env["res.users"].browse(2)
        attachment = (
            self.env["ir.attachment"]
            .with_user(test_user)
            .create(
                {
                    "name": "Test Attachment",
                    "datas": file.datas,
                    "res_model": "sale.order",
                    "res_id": self.sale_order.id,
                    "website_id": 1,
                }
            )
        )
        self.sale_order.action_confirm()
        fsm_attachments = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "fsm.order"),
                ("res_id", "=", self.get_active_fsm_order().id),
            ]
        )
        self.assertTrue(fsm_attachments)
        self.assertEqual(fsm_attachments[0].name, attachment.name)
        self.assertEqual(fsm_attachments[0].datas, attachment.datas)
