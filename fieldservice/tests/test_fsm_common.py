from odoo.tests.common import TransactionCase


class FSMCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Setup common test partners and sub-partners
        cls.test_partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "phone": "1234567890",
                "email": "tp@email.com",
            }
        )
        cls.parent_partner = cls.env["res.partner"].create(
            {
                "name": "Parent Partner",
                "type": "contact",
            }
        )
        cls.sub_partner_1 = cls.env["res.partner"].create(
            {
                "name": "Sub Partner 1",
                "type": "contact",
                "parent_id": cls.parent_partner.id,
            }
        )
        cls.sub_partner_2 = cls.env["res.partner"].create(
            {
                "name": "Sub Partner 2",
                "type": "invoice",
                "parent_id": cls.parent_partner.id,
            }
        )
        cls.sub_partner_3 = cls.env["res.partner"].create(
            {
                "name": "Sub Partner 3",
                "type": "delivery",
                "parent_id": cls.parent_partner.id,
            }
        )
        cls.sub_partner_4 = cls.env["res.partner"].create(
            {
                "name": "Sub Partner 4",
                "type": "other",
                "parent_id": cls.parent_partner.id,
            }
        )

        # Setup common partner locations
        cls.test_loc_partner = cls.env["res.partner"].create(
            {
                "name": "Test Loc Partner",
                "phone": "ABC",
                "email": "tlp@email.com",
            }
        )
        cls.location_partner_1 = cls.env["res.partner"].create(
            {
                "name": "Loc Partner 1",
            }
        )
        cls.location_partner_2 = cls.env["res.partner"].create(
            {
                "name": "Loc Partner 2",
            }
        )
        cls.location_partner_3 = cls.env["res.partner"].create(
            {
                "name": "Loc Partner 3",
            }
        )

        # Setup common stages for equipment
        cls.equipment_stage_1 = cls.env["fsm.stage"].create(
            {
                "name": "Equipment Stage 1",
                "sequence": 1,
                "stage_type": "equipment",
            }
        )
        cls.equipment_stage_2 = cls.env["fsm.stage"].create(
            {
                "name": "Equipment Stage 2",
                "sequence": 2,
                "stage_type": "equipment",
            }
        )
        cls.equipment_stage_3 = cls.env["fsm.stage"].create(
            {
                "name": "Equipment Stage 3",
                "sequence": 3,
                "stage_type": "equipment",
            }
        )

        # Setup common stages for location
        cls.location_stage_1 = cls.env["fsm.stage"].create(
            {
                "name": "Location Stage 1",
                "sequence": 1,
                "stage_type": "location",
            }
        )
        cls.location_stage_2 = cls.env["fsm.stage"].create(
            {
                "name": "Location Stage 2",
                "sequence": 2,
                "stage_type": "location",
            }
        )
        cls.location_stage_3 = cls.env["fsm.stage"].create(
            {
                "name": "Location Stage 3",
                "sequence": 3,
                "stage_type": "location",
            }
        )

        # Setup common stages for worker
        cls.worker_stage_1 = cls.env["fsm.stage"].create(
            {
                "name": "Worker Stage 1",
                "sequence": 1,
                "stage_type": "worker",
            }
        )
        cls.worker_stage_2 = cls.env["fsm.stage"].create(
            {
                "name": "Worker Stage 2",
                "sequence": 2,
                "stage_type": "worker",
            }
        )
        cls.worker_stage_3 = cls.env["fsm.stage"].create(
            {
                "name": "Worker Stage 3",
                "sequence": 3,
                "stage_type": "worker",
            }
        )

        # Setup common persons
        cls.test_person = cls.env["fsm.person"].create(
            {
                "name": "Test Person",
                "phone": "1234567890",
                "email": "tp@email.com",
            }
        )
        cls.person_1 = cls.env["fsm.person"].create(
            {
                "name": "Person 1",
            }
        )
        cls.person_2 = cls.env["fsm.person"].create(
            {
                "name": "Person 2",
            }
        )
        cls.person_3 = cls.env["fsm.person"].create(
            {
                "name": "Person 3",
            }
        )

        # Setup common territories
        cls.test_region = cls.env["res.region"].create(
            {
                "name": "Test Region",
            }
        )
        cls.test_district = cls.env["res.district"].create(
            {
                "name": "Test District",
                "region_id": cls.test_region.id,
            }
        )
        cls.test_branch = cls.env["res.branch"].create(
            {
                "name": "Test Branch",
                "district_id": cls.test_district.id,
            }
        )
        cls.test_territory = cls.env["res.territory"].create(
            {
                "name": "Test Territory",
                "branch_id": cls.test_branch.id,
            }
        )

        # Setup common locations
        cls.test_location = cls.env["fsm.location"].create(
            {
                "name": "Test Location",
                "phone": "1234567890",
                "email": "tp@email.com",
                "partner_id": cls.test_loc_partner.id,
                "owner_id": cls.test_loc_partner.id,
                "territory_id": cls.test_territory.id,
                "branch_id": cls.test_branch.id,
                "district_id": cls.test_district.id,
                "region_id": cls.test_region.id,
                "direction": "Test Direction",
                "street": "123 Test St",
                "street2": "Suite 100",
            }
        )
        cls.location_1 = cls.env["fsm.location"].create(
            {
                "name": "Location 1",
                "partner_id": cls.location_partner_1.id,
                "owner_id": cls.location_partner_1.id,
            }
        )
        cls.location_2 = cls.env["fsm.location"].create(
            {
                "name": "Location 2",
                "partner_id": cls.location_partner_2.id,
                "owner_id": cls.location_partner_2.id,
            }
        )
        cls.location_3 = cls.env["fsm.location"].create(
            {
                "name": "Location 3",
                "partner_id": cls.location_partner_3.id,
                "owner_id": cls.location_partner_3.id,
            }
        )

    def normalize_domain(self, d):
        return list(d)
