# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import TransactionCase, tagged

from ..hooks import post_init_hook


@tagged("post_install", "-at_install")
class FSMOrderHistoricalLocations(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location = cls.env.ref("fieldservice.test_location")
        cls.order = cls.env["fsm.order"].create(
            {
                "location_id": cls.location.id,
                "date_end": datetime.today(),
                "resolution": "Test resolution",
            }
        )

    def test_post_init_hook(self):
        post_init_hook(self.env)
        self.assertEqual(self.order.street, self.location.street)
        self.assertEqual(self.order.street2, self.location.street2)
        self.assertEqual(self.order.zip, self.location.zip)
        self.assertEqual(self.order.city, self.location.city)
        self.assertEqual(
            self.order.state_name,
            self.location.state_id.name if self.location.state_id else False,
        )
        self.assertEqual(
            self.order.country_name,
            self.location.country_id.name if self.location.country_id else False,
        )

    def test_compute_location_id_fields(self):
        self.order.action_complete()
        self.location.street = "Test Street"
        self.assertNotEqual(self.order.street, self.location.street)
