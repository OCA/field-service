# Copyright (C) 2019 Clément Mombereau (Akretion)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests.common import TransactionCase


class FSMSale(TransactionCase):
    def setUp(self):
        """Create 3 related partners : a parent company, a child partner and
        a child shipping partner.

        For each test, a different partner is a fsm_location.
        A SO is created with the child partner as customer. The test run
        the SO's onchange_partner_id and check if the fsm_location_id
        is the expected one.
        """
        super(FSMSale, self).setUp()
        # create a parent company
        self.commercial_partner = self.env["res.partner"].create(
            {
                "name": "Company Commercial Partner",
                "is_company": True,
            }
        )
        # create a child partner
        self.partner = self.env["res.partner"].create(
            {
                "name": "Child Partner",
                "parent_id": self.commercial_partner.id,
            }
        )
        # create a child partner shipping address
        self.shipping_partner = self.env["res.partner"].create(
            {
                "name": "Shipping Partner",
                "parent_id": self.commercial_partner.id,
                "type": "delivery",
            }
        )
        # Demo FS location
        self.location = self.env.ref("fieldservice.location_1")

    def test_1_autofill_so_fsm_location(self):
        """First case :
        - commercial_partner IS NOT a fsm_location
        - partner IS a fsm_location
        - shipping_partner IS NOT a fsm_location
        Test if the SO's fsm_location_id is autofilled with the expected
        partner_location.
        """
        # Link demo FS location to self.partner
        self.location.partner_id = self.partner.id
        # create a Sale Order and run onchange_partner_id
        self.so = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.so.onchange_partner_id()
        self.assertEqual(self.so.fsm_location_id.id, self.location.id)

    def test_2_autofill_so_fsm_location(self):
        """Second case :
        - commercial_partner IS NOT a fsm_location
        - partner IS NOT a fsm_location
        - shipping_partner IS a fsm_location
        Test if the SO's fsm_location_id is autofilled with the expected
        shipping_partner_location.
        """
        # Link demo FS location to self.shipping_partner
        self.location.partner_id = self.shipping_partner.id
        # create a Sale Order and run onchange_partner_id
        self.so = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.so.onchange_partner_id()
        self.assertEqual(self.so.fsm_location_id.id, self.location.id)

    def test_3_autofill_so_fsm_location(self):
        """Third case :
        - commercial_partner IS a fsm_location
        - partner IS NOT a fsm_location
        - shipping_partner IS NOT a fsm_location
        Test if the SO's fsm_location_id is autofilled with the expected
        commercial_partner_location.
        """
        # Link demo FS location to self.commercial_partner
        self.location.partner_id = self.commercial_partner.id
        # create a Sale Order and run onchange_partner_id
        self.so = self.env["sale.order"].create({"partner_id": self.partner.id})
        self.so.onchange_partner_id()
        self.assertEqual(self.so.fsm_location_id.id, self.location.id)
