# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Domain

from .test_fsm_common import FSMCommon


class FSMPerson(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Worker = cls.env["fsm.person"]
        cls.LocationWorker = cls.env["fsm.location.person"]

    def test_fsm_person(self):
        # Create a person
        test_worker_one = self.Worker.create({"name": "Worker One"})
        self.assertTrue(test_worker_one.fsm_person)
        # Test archive/unarchive
        test_worker_one.action_archive()
        self.assertTrue(
            test_worker_one.partner_id.active,
            "Partner related to FSM Person should remain active",
        )
        test_worker_one.partner_id.action_archive()
        test_worker_one.action_unarchive()
        self.assertTrue(
            test_worker_one.partner_id.active,
            "Activating FSM Person must make related partner active",
        )

    def test_fsm_person_search(self):
        # Setup locations
        location_1 = self.location_1
        location_2 = self.location_2
        location_3 = self.location_3
        # Setup Persons
        person_1 = self.person_1
        person_2 = self.person_2
        person_3 = self.person_3
        # Setup Location Persons
        self.LocationWorker.create(
            {
                "location_id": location_1.id,
                "person_id": person_1.id,
            }
        )
        self.LocationWorker.create(
            {
                "location_id": location_2.id,
                "person_id": person_2.id,
            }
        )
        self.LocationWorker.create(
            {
                "location_id": location_3.id,
                "person_id": person_3.id,
            }
        )
        # Test search using a location ID
        search_domain = Domain("location_ids", "=", location_2.id)
        workers = self.Worker.search(search_domain)
        self.assertEqual(workers[:1].id, person_2.id)
        # Test search using a location name
        search_domain = Domain("location_ids", "=", "Location")
        workers = self.Worker.search(search_domain)
        self.assertEqual(len(workers), 3, "Incorrect search number result")
