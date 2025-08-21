# Copyright (C) 2025 APSL-Nagarro Bernat Obrador bobrador@apsl.net
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import os

from odoo.tests.common import TransactionCase


class TestFSMOrderSignatureWizard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Cliente Ejemplo",
            }
        )

        location_vals = {
            "name": "Test Location",
            "partner_id": cls.partner.id,
            "owner_id": cls.partner.id,
        }
        if (
            cls.env["ir.module.module"]
            .search([("name", "=", "fieldservice_account_analytic")])
            .state
            == "installed"
        ):
            location_vals["customer_id"] = cls.partner.id

        cls.location = cls.env["fsm.location"].create(location_vals)

        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )

        cls.fsm_order = cls.env["fsm.order"].create(
            {
                "location_id": cls.location.id,
                "sale_id": cls.sale_order.id,
            }
        )

    def test_signature_confirmation_sets_fields(self):
        signature_data = self.get_signature_from_file()

        wizard = self.env["fsm.order.signature.wizard"].create(
            {
                "fsm_order_id": self.fsm_order.id,
                "signature": signature_data,
            }
        )

        wizard.action_confirm()

        self.assertEqual(self.fsm_order.signature, signature_data)
        self.assertEqual(self.fsm_order.signed_by, self.partner.name)
        self.assertTrue(self.fsm_order.signed_on)

        self.assertEqual(self.sale_order.signature, signature_data)
        self.assertEqual(self.sale_order.signed_by, self.partner.name)
        self.assertTrue(self.sale_order.signed_on)

        self.assertEqual(self.fsm_order.sale_id.signature, self.fsm_order.signature)
        self.assertEqual(self.fsm_order.sale_id.signed_by, self.fsm_order.signed_by)
        self.assertEqual(self.fsm_order.sale_id.signed_on, self.fsm_order.signed_on)

    def test_signature_confirmation_without_sale_order(self):
        self.fsm_order.sale_id = False
        signature_data = self.get_signature_from_file()

        wizard = self.env["fsm.order.signature.wizard"].create(
            {
                "fsm_order_id": self.fsm_order.id,
                "signature": signature_data,
            }
        )

        wizard.action_confirm()

        self.assertEqual(self.fsm_order.signature, signature_data)
        self.assertEqual(self.fsm_order.signed_by, self.partner.name)
        self.assertTrue(self.fsm_order.signed_on)

        self.assertFalse(self.sale_order.signature)

    def get_signature_from_file(self):
        """Load a test PNG signature file and return base64 binary."""
        path = os.path.join(os.path.dirname(__file__), "static", "test_signature.png")
        with open(path, "rb") as f:
            return base64.b64encode(f.read())
