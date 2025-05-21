# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.website.tools import MockRequest

from ..controllers.main import WebsiteSale


class TestFSMWebsiteSaleCheckoutAddressFilter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.WebsiteSale = WebsiteSale()
        cls.website = cls.env.ref("website.default_website")
        cls.partner_demo = cls.env.ref("fieldservice.test_loc_partner")
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.user_demo = cls._create_portal_user(cls.partner_demo)
        cls.user_demo.action_grant_access()
        cls.user_demo = cls.env["res.users"].search(
            [("email", "=", cls.user_demo.email)]
        )

        cls.child1 = cls.env["res.partner"].create(
            {
                "name": "Valid Shipping Addr",
                "parent_id": cls.partner_demo.id,
                "type": "delivery",
                "email": "ship1@example.com",
                "website_id": cls.website.id,
            }
        )

        cls.invalid_child = cls.env["res.partner"].create(
            {
                "name": "Invalid Shipping Addr",
                "parent_id": cls.partner_demo.id,
                "type": "delivery",
                "email": "invalid@example.com",
                "website_id": cls.website.id,
            }
        )

        cls.fsm_route = cls.env["fsm.route"].create(
            {
                "name": "Route 1",
                "fsm_person_id": cls.env.ref("fieldservice.test_person").id,
                "max_order": 5,
                "day_ids": [
                    (6, 0, [cls.env.ref("fieldservice_route.fsm_route_day_0").id])
                ],
            }
        )

        cls.fsm_route_parent = cls.env["fsm.route"].create(
            {
                "name": "Route 2",
                "fsm_person_id": cls.env.ref("fieldservice.test_person").id,
                "max_order": 20,
                "day_ids": [
                    (6, 0, [cls.env.ref("fieldservice_route.fsm_route_day_1").id])
                ],
            }
        )

        cls.env["fsm.location"].create(
            {
                "name": "Location 1",
                "owner_id": cls.child1.id,
                "partner_id": cls.child1.id,
                "customer_id": cls.child1.id,
                "fsm_route_id": cls.fsm_route.id,
            }
        )

        cls.test_location.write({"fsm_route_id": cls.fsm_route_parent.id})

        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner_demo.id,
                "website_id": cls.website.id,
            }
        )

    @classmethod
    def _create_portal_user(cls, partner):
        """Return a portal wizard user from a partner."""
        portal_wizard = (
            cls.env["portal.wizard"].with_context(active_ids=[partner.id]).create({})
        )
        return portal_wizard.user_ids

    def test_fsm_filter_shipping_addresses(self):
        """Only show addresses linked to valid FSM locations."""
        with MockRequest(
            self.order.with_user(self.user_demo).env,
            website=self.website.with_user(self.user_demo),
        ):
            vals = self.WebsiteSale.checkout_values()
        ids = vals["shippings"].mapped("id")

        self.assertIn(self.partner_demo.id, ids)
        self.assertIn(self.child1.id, ids)
        self.assertNotIn(self.invalid_child.id, ids)
