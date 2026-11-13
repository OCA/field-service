# Copyright (C) 2023, Brian McMaster
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Domain

from .test_fsm_common import FSMCommon


class FSMResPartner(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location_1_partner = cls.location_1.partner_id
        cls.loc_1 = cls.env["fsm.location"].create(
            {"name": "Test Location 1", "owner_id": cls.sub_partner_1.id}
        )
        cls.loc_2 = cls.env["fsm.location"].create(
            {"name": "Test Location 2", "owner_id": cls.sub_partner_2.id}
        )

    def test_res_partner_open_owned_locations(self):
        # Test with one owner location
        action = self.location_1_partner.action_open_owned_locations()
        self.assertEqual(action["res_id"], self.location_1.id)

        # Test with multiple owned locations
        expected_domain = Domain("id", "in", [self.loc_1.id, self.loc_2.id])
        action = self.parent_partner.action_open_owned_locations()
        self.assertEqual(action["domain"], expected_domain)

    def test_action_open_owned_locations_empty(self):
        partner = self.env["res.partner"].create({"name": "No Locations"})
        action = partner.action_open_owned_locations()
        self.assertEqual(action["res_model"], "fsm.location")
        self.assertFalse(action.get("res_id"))
        self.assertFalse(action.get("domain"))
        # Empty recordset: loop body is skipped.
        self.assertFalse(self.env["res.partner"].action_open_owned_locations())

    def test_partner_convert_to_location_action(self):
        self.test_partner.action_fsm_convert_to_location()
        self.assertTrue(self.test_partner.fsm_location)
        self.assertTrue(self.test_partner.fsm_location_ids)

    def test_partner_convert_to_person_action(self):
        partner = self.env["res.partner"].create({"name": "Convert To Worker"})
        partner.action_fsm_convert_to_person()
        self.assertTrue(partner.fsm_person)
        self.assertTrue(
            self.env["fsm.person"].search(Domain("partner_id", "=", partner.id))
        )

    def test_partner_write_type_fsm_location(self):
        partner = self.env["res.partner"].create(
            {
                "parent_id": self.parent_partner.id,
                "name": "Written As Location",
                "type": "contact",
            }
        )
        partner.write({"type": "fsm_location"})
        self.assertTrue(partner.fsm_location_ids)
