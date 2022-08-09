# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class FSMPerson(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Worker = self.env["fsm.person"]

    def test_fsm_person(self):
        """Test creating new person
        - Default stage
        - Change stage
        - _search
        """
        # Create a person
        view_id = "fieldservice.fsm_person_form"
        with Form(self.Worker, view=view_id) as f:
            f.name = "Worker A"
        worker = f.save()
        location_owner = self.env.ref("fieldservice.location_partner_1")
        location = self.env["fsm.location"].create(
            {"name": "test location", "owner_id": location_owner.id}
        )
        parent_partner = self.env.ref("fieldservice.test_parent_partner")
        sub_p = self.env.ref("fieldservice.s1")
        sub_p1 = self.env.ref("fieldservice.s2")
        self.env["fsm.location"].create({"name": "test location", "owner_id": sub_p.id})
        parent_partner.action_open_owned_locations()
        self.env["fsm.location"].create(
            {"name": "test location", "owner_id": sub_p1.id}
        )
        parent_partner.action_open_owned_locations()
        self.test_team = self.env["fsm.team"].create({"name": "Test Team"})
        person_id = self.env.ref("fieldservice.person_1").id
        self.env["fsm.location.person"].create(
            {
                "location_id": location.id,
                "person_id": person_id,
            }
        )
        search_domain = [("location_ids", "=", location.id)]
        data = (
            self.env["fsm.person"]
            .with_user(self.env.user)
            .read_group(
                [("id", "=", location.id)], fields=["stage_id"], groupby="stage_id"
            )
        )
        self.assertTrue(data, "It should be able to read group")
        p1 = self.Worker.search(search_domain)
        search_domain = [("location_ids", "=", "Test")]
        self.Worker.search(search_domain)
        self.assertEqual(p1.id, person_id)
        # Test change state
        worker.stage_id = self.env.ref("fieldservice.worker_stage_1")
        worker.next_stage()
        self.assertEqual(worker.stage_id, self.env.ref("fieldservice.worker_stage_2"))
        worker.stage_id = self.env.ref("fieldservice.worker_stage_3")
        worker.next_stage()
        self.assertEqual(worker.stage_id, self.env.ref("fieldservice.worker_stage_3"))
        self.assertFalse(worker.hide)  # hide as max stage
        worker.stage_id = self.env.ref("fieldservice.worker_stage_2")
        worker.previous_stage()
        self.assertEqual(worker.stage_id, self.env.ref("fieldservice.worker_stage_1"))

        # TODO: https://github.com/OCA/field-service/issues/265
