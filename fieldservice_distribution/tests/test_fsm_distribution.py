# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestFSMSDistribution(TransactionCase):
    def setUp(self):
        super(TestFSMSDistribution, self).setUp()
        self.location = self.env["fsm.location"]
        self.FSMOrder = self.env["fsm.order"]
        self.test_loc_partner = self.env["res.partner"].create(
            {"name": "Test Loc Partner 2", "phone": "123", "email": "tlp@example.com"}
        )
        self.test_location = self.env.ref("fieldservice.test_location")
        self.test_location2 = self.location.create(
            {
                "name": "Test Location 2",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
                "dist_parent_id": self.test_location.id,
                "is_a_distribution": True,
            }
        )
        self.test_location3 = self.location.create(
            {
                "name": "Test Location 2",
                "phone": "123",
                "email": "tp@email.com",
                "partner_id": self.test_loc_partner.id,
                "owner_id": self.test_loc_partner.id,
            }
        )

    def test_fsm_location(self):
        """Test creating new location, and test following functions."""
        self.test_location._compute_distrib_sublocation_ids()
        self.test_location.action_view_distrib_sublocation()
        self.test_location3.action_view_distrib_sublocation()
