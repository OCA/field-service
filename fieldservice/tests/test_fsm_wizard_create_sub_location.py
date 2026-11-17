# Copyright (C) 2025 - TODAY, APSL - Nagarro (Bernat Obrador)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.fieldservice.tests.common import MockGeocoderCase


@tagged("post_install", "-at_install")
class TestCreateSubLocationWizard(MockGeocoderCase, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        location_vals = {
            "name": "Main Location",
            "owner_id": cls.env.ref("base.res_partner_1").id,
        }
        if cls.env["ir.module.module"].search(
            [
                ("name", "=", "fieldservice_account_analytic"),
                ("state", "=", "installed"),
            ]
        ):
            location_vals.update({"customer_id": cls.env.ref("base.res_partner_1").id})

        cls.location = cls.env["fsm.location"].create(
            location_vals,
        )

    def test_create_sub_location(self):
        (
            self.env["fsm.create.sub.location.wizard"]
            .sudo()
            .create(
                {
                    "parent_location_id": self.location.id,
                    "related_owner_id": self.env.ref("base.res_partner_1").id,
                    "street": "Sub location street",
                }
            )
        ).create_sub_location()

        sub_location = self.env["fsm.location"].search(
            [("fsm_parent_id", "=", self.location.id)]
        )
        self.assertTrue(sub_location)
        self.assertTrue(len(sub_location) == 1)
        self.assertEqual(
            sub_location.name,
            f"{self.location.name} - {sub_location.street}",
        )
