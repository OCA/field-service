# Copyright (C) 2019 Clément Mombereau (Akretion)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests.common import Form, TransactionCase


class FSMSale(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """Create 3 related partners : a parent company, a child partner and
        a child shipping partner.

        For each test, a different partner is a fsm_location.
        A SO is created with the child partner as customer. The test run
        the SO's location autofill and check if the fsm_location_id
        is the expected one.
        """
        super().setUpClass()
        # create a parent company
        cls.commercial_partner = cls.env["res.partner"].create(
            {"name": "Company Commercial Partner", "is_company": True}
        )
        # create a child partner
        cls.partner = cls.env["res.partner"].create(
            {"name": "Child Partner 1", "parent_id": cls.commercial_partner.id}
        )
        # create a child partner shipping address
        cls.shipping_partner = cls.env["res.partner"].create(
            {
                "name": "Shipping Partner",
                "parent_id": cls.commercial_partner.id,
                "type": "delivery",
            }
        )
        # Demo FS location
        cls.location1 = cls.env.ref("fieldservice.location_1")
        cls.location2 = cls.env.ref("fieldservice.location_2")
        cls.location3 = cls.env.ref("fieldservice.location_3")

    def test_00_autofill_so_fsm_location(self):
        """Check location autofill from SO partner

        SO partner is an FSM location linked to location 2 => expect location2
        (location 1 and 3 are ignored because we want only location explicitly
        linked to the partner)
        """
        self.partner.fsm_location = True
        self.location1.partner_id = self.commercial_partner
        self.location2.partner_id = self.partner
        self.location3.partner_id = self.shipping_partner
        with Form(self.env["sale.order"]) as so_form:
            so_form.partner_id = self.partner
        so = so_form.save()
        self.assertEqual(so.fsm_location_id, self.location2)

    def test_01_autofill_so_fsm_location(self):
        """Check location autofill from SO partner

        SO partner is not an FSM location defined, but location1 is linked to
        its commercial partner => expect location 1 (because of ordering)
        """
        self.partner.fsm_location = False
        self.location1.partner_id = self.commercial_partner
        self.location2.partner_id = self.partner
        self.location3.partner_id = self.shipping_partner
        with Form(self.env["sale.order"]) as so_form:
            so_form.partner_id = self.partner
        so = so_form.save()
        self.assertEqual(so.fsm_location_id, self.location1)

    def test_02_autofill_so_fsm_location(self):
        """Check location autofill from SO partner

        SO partner is not an FSM location defined, but location1 is linked to
        the partner itself => expect location 1 (because of ordering)
        """
        self.partner.fsm_location = False
        self.location1.partner_id = self.partner
        self.location2.partner_id = self.shipping_partner
        self.location3.partner_id = self.commercial_partner
        with Form(self.env["sale.order"]) as so_form:
            so_form.partner_id = self.partner
        so = so_form.save()
        self.assertEqual(so.fsm_location_id, self.location1)

    def test_03_autofill_so_fsm_location(self):
        """Check location autofill from SO partner

        SO partner is not an FSM location defined, but location1 is linked to
        its shipping partner => expect location 1 (because of ordering)
        """
        self.partner.fsm_location = False
        self.location1.partner_id = self.shipping_partner
        self.location2.partner_id = self.commercial_partner
        self.location3.partner_id = self.partner
        with Form(self.env["sale.order"]) as so_form:
            so_form.partner_id = self.partner
        so = so_form.save()
        self.assertEqual(so.fsm_location_id, self.location1)
