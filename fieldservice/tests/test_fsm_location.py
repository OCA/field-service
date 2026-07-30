# Copyright (C) 2019 - TODAY, Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.fields import Domain
from odoo.tests import Form

from .test_fsm_common import FSMCommon


class FSMLocation(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Location = cls.env["fsm.location"]
        cls.Equipment = cls.env["fsm.equipment"]

    def test_fsm_location(self):
        """Test createing new location
        - Onchange parent, will get all parent info
        - Default stage
        - Change stage
        - Create fsm.location.person if auto_populate_persons_on_location
        """
        # Create an equipment
        self.env.user.group_ids += self.env.ref("fieldservice.group_fsm_territory")
        view_id = "fieldservice.fsm_location_form_view"
        with Form(self.Location, view=view_id) as f:
            f.name = "Child Location"
            f.parent_id = self.test_location
        location = f.save()
        # Test child location equal to parent location
        for x in [
            "owner_id",
            "contact_id",
            "direction",
            "street",
            "street2",
            "city",
            "zip",
            "state_id",
            "country_id",
            "tz",
            "territory_id",
        ]:
            self.assertEqual(location[x], self.test_location[x])

        # Check partner defaults.
        self.assertTrue(location.fsm_location)
        self.assertFalse(location.fsm_person)
        self.assertFalse(location.is_company)
        self.assertEqual(location.partner_id.parent_id, self.test_loc_partner)
        self.assertNotEqual(location.partner_id, self.test_loc_partner)
        self.assertEqual(location.type, "fsm_location")

        # Test initial stage
        self.assertEqual(location.stage_id, self.location_stage_1)
        # Test change state
        location.next_stage()
        self.assertEqual(location.stage_id, self.location_stage_2)
        location.stage_id = self.location_stage_3
        location.next_stage()
        self.assertEqual(location.stage_id, self.location_stage_3)
        self.assertFalse(location.hide)  # hide as max stage
        location.stage_id = self.location_stage_2
        location.previous_stage()
        self.assertEqual(location.stage_id, self.location_stage_1)
        # Test create fsm.location.person, when has if territory has person_ids
        self.env.company.auto_populate_persons_on_location = True
        person_ids = [self.person_1.id, self.person_2.id, self.person_3.id]
        self.test_territory.write({"person_ids": [(6, 0, person_ids)]})
        location.territory_id = self.test_territory
        self.assertEqual(len(location.person_ids), 0)
        location._onchange_territory_id()
        self.assertEqual(len(location.person_ids), 3)
        res = location.owner_id.action_open_owned_locations()
        domain = self.normalize_domain(res["domain"])
        self.assertIn(location.id, domain[0][2])
        self.location_1.parent_id = self.test_location
        self.location_1.ref = "Test Ref"
        self.location_3.ref = "Test Ref3"
        self.location_1._compute_complete_name()
        self.location_2._compute_complete_name()
        self.location_3._compute_complete_name()
        self.location_3.geo_localize()
        self.location_2.state_id = self.env.ref("base.state_au_1").id
        self.location_2.country_id = self.env.ref("base.af").id
        self.location_2._onchange_country_id()
        self.location_1.state_id = self.env.ref("base.state_au_1").id
        self.location_1._onchange_state()
        self.assertEqual(
            self.location_1.country_id.id, self.location_1.state_id.country_id.id
        )
        data = (
            self.env["fsm.location"]
            .with_user(self.env.user)
            ._read_group(
                domain=Domain("id", "=", location.id),
                groupby=["stage_id"],
                aggregates=["__count"],
            )
        )
        self.assertTrue(data, "It should be able to read group")

    def test_fsm_multi_sublocation(self):
        """Test create location with many sub locations
        - Test recursion exceptoin
        - Test count all equipments, contacts, sublocations
        """
        # Test Location > Location 1 > Location 2 > Location 3
        self.location_3.parent_id = self.location_2
        self.location_2.parent_id = self.location_1
        self.location_1.parent_id = self.test_location
        # Test sublocation_count of each level
        self.assertEqual(
            (
                self.test_location.sublocation_count,
                self.location_1.sublocation_count,
                self.location_2.sublocation_count,
                self.location_3.sublocation_count,
            ),
            (3, 2, 1, 0),
        )

        location_0_sublocations = self.env["fsm.location"].search(
            self.test_location.action_view_sublocation()["domain"]
        )
        self.assertEqual(
            location_0_sublocations, self.location_1 + self.location_2 + self.location_3
        )

        location_1_sublocations = self.env["fsm.location"].search(
            self.location_1.action_view_sublocation()["domain"]
        )
        self.assertEqual(location_1_sublocations, self.location_2 + self.location_3)

        location_2_sublocations = (
            self.env["fsm.location"]
            .browse(self.location_2.action_view_sublocation()["res_id"])
            .exists()
        )
        self.assertEqual(location_2_sublocations, self.location_3)

        # Test recursion exception
        with (
            self.assertRaisesRegex(UserError, "Recursion Detected"),
            self.env.cr.savepoint(),
        ):
            self.test_location.parent_id = self.location_3

        # Add equipments on each locations, and test counting
        location_vs_num_eq = {
            self.test_location.id: 1,  # Topup = 9
            self.location_1.id: 1,  # Topup = 8
            self.location_2.id: 5,  # Topup = 7
            self.location_3.id: 1,
        }  # Topup = 2
        for loc_id, num_eq in location_vs_num_eq.items():
            for i in range(num_eq):
                self.Equipment.create(
                    {
                        "name": f"Eq-{str(loc_id)}-{str(i + 1)}",
                        "location_id": loc_id,
                        "current_location_id": loc_id,
                    }
                )
        # Test valid equipments at each location
        self.assertEqual(
            (
                self.test_location.equipment_count,
                self.location_1.equipment_count,
                self.location_2.equipment_count,
                self.location_3.equipment_count,
            ),
            (8, 7, 6, 1),
        )  # !!
        # Test smart button to open equipment
        location_0_equipment = self.env["fsm.equipment"].search(
            self.test_location.action_view_equipment()["domain"]
        )
        location_1_equipment = self.env["fsm.equipment"].search(
            self.location_1.action_view_equipment()["domain"]
        )
        location_2_equipment = self.env["fsm.equipment"].search(
            self.location_2.action_view_equipment()["domain"]
        )
        location_3_equipment = (
            self.env["fsm.equipment"]
            .browse(self.location_3.action_view_equipment()["res_id"])
            .exists()
        )

        self.assertEqual(len(location_0_equipment), 8)
        self.assertEqual(len(location_1_equipment), 7)
        self.assertEqual(len(location_2_equipment), 6)
        self.assertEqual(len(location_3_equipment), 1)

        self.test_loc_partner._compute_owned_location_count()
        # Set service_location_id, on relavant res.partner, test contact count
        self.test_loc_partner.service_location_id = self.test_location
        self.location_partner_1.service_location_id = self.location_1
        self.location_partner_2.service_location_id = self.location_2
        self.location_partner_3.service_location_id = self.location_3
        # Test valid contacts at each location
        self.assertEqual(
            (
                self.test_location.contact_count,
                self.location_1.contact_count,
                self.location_2.contact_count,
                self.location_3.contact_count,
            ),
            (4, 3, 2, 1),
        )
        # Test smart button to open contacts
        location_0_contacts = self.env["res.partner"].search(
            self.test_location.action_view_contacts()["domain"]
        )
        location_1_contacts = self.env["res.partner"].search(
            self.location_1.action_view_contacts()["domain"]
        )
        location_2_contacts = self.env["res.partner"].search(
            self.location_2.action_view_contacts()["domain"]
        )
        location_3_contacts = (
            self.env["res.partner"]
            .browse(self.location_3.action_view_contacts()["res_id"])
            .exists()
        )
        self.assertEqual(len(location_0_contacts), 4)
        self.assertEqual(len(location_1_contacts), 3)
        self.assertEqual(len(location_2_contacts), 2)
        self.assertEqual(len(location_3_contacts), 1)

    def test_convert_partner_to_fsm_location(self):
        """
        FSM Location can be created from the res.partner form
        like invoice addresses or delivery addresses.
        child of partner with type = fsm_location
        """
        # ensure no regression on classic types
        contact = self.env["res.partner"].create(
            {
                "parent_id": self.test_partner.id,
                "name": "A contact",
                "type": "contact",
            }
        )
        self.assertFalse(contact.fsm_location)
        no_type = self.env["res.partner"].create(
            {
                "parent_id": self.test_partner.id,
                "name": "A contact",
            }
        )
        self.assertFalse(no_type.fsm_location)

        # test with type = fsm_location
        vals = {
            "parent_id": self.test_partner.id,
            "name": "A location",
            "type": "fsm_location",
        }
        child_loc = self.env["res.partner"].create(vals)

        self.assertTrue(child_loc.fsm_location, "fsm_location Flag should be set")
        self.assertTrue(child_loc.fsm_location_ids, "fsm.location should exist")
        self.assertEqual(
            child_loc.fsm_location_ids.partner_id,
            child_loc,
            "ensure circular references",
        )

    def test_convert_partner_to_fsm_location_multi(self):
        """
        Ensure behavior in create_multi
        """
        vals = [
            {"parent_id": self.test_partner.id, "type": "invoice", "name": "contact"},
            {
                "parent_id": self.test_partner.id,
                "type": "fsm_location",
                "name": "location",
            },
        ]
        children_loc = self.env["res.partner"].create(vals)
        self.assertEqual(len(children_loc.filtered("fsm_location")), 1)

        # ensure archive is still possible
        children_loc.action_archive()
        self.assertTrue(
            self.env["res.partner"].search(
                Domain("active", "=", False) & Domain("id", "in", children_loc.ids)
            )
        )

    def test_create_root_fsm_location(self):
        """Root locations can be created without an existing partner."""
        location = self.Location.create({"name": "Root Location"})
        self.assertTrue(location.fsm_location)
        self.assertEqual(location.type, "fsm_location")
        self.assertEqual(location.owner_id, location.partner_id)
        self.assertFalse(location.partner_id.parent_id)

    def test_create_root_fsm_location_from_form(self):
        """Root locations can be saved from the UI without owner or partner."""
        with Form(self.Location, view="fieldservice.fsm_location_form_view") as f:
            f.name = "Root Location From Form"
        location = f.save()
        self.assertEqual(location.owner_id, location.partner_id)

    def test_child_partner_location_gets_parent_fsm_location(self):
        """Child location partners inherit the parent contact FSM location."""
        self.env["fsm.wizard"].action_convert_location(self.test_partner)
        parent_location = self.test_partner.fsm_location_ids[:1]
        child_loc = self.env["res.partner"].create(
            {
                "parent_id": self.test_partner.id,
                "name": "Child Location",
                "type": "fsm_location",
            }
        )
        child_fsm_location = child_loc.fsm_location_ids[:1]
        self.assertEqual(child_fsm_location.parent_id, parent_location)
        self.assertEqual(child_fsm_location.owner_id, self.test_partner)

    def test_create_sublocation_inherits_owner_from_parent(self):
        """Sub-locations without owner inherit it from the parent location."""
        location = self.Location.create(
            {
                "name": "Sub Without Owner",
                "parent_id": self.test_location.id,
            }
        )
        self.assertEqual(location.owner_id, self.test_location.owner_id)
        self.assertEqual(location.partner_id.parent_id, self.test_location.owner_id)

    def test_create_sublocation_from_form(self):
        """Sub-locations created from the form inherit owner and partner parent."""
        with Form(self.Location, view="fieldservice.fsm_location_form_view") as f:
            f.name = "Child From Form"
            f.parent_id = self.test_location
        location = f.save()
        self.assertEqual(location.owner_id, self.test_location.owner_id)
        self.assertEqual(location.partner_id.parent_id, self.test_location.owner_id)

    def test_create_location_with_existing_partner(self):
        """Creating with an existing partner must not overwrite partner parent."""
        partner = self.env["res.partner"].create({"name": "Existing Loc Partner"})
        location = self.Location.create(
            {
                "name": "Existing Partner Location",
                "partner_id": partner.id,
                "owner_id": partner.id,
            }
        )
        self.assertEqual(location.partner_id, partner)
        self.assertFalse(location.partner_id.parent_id)
