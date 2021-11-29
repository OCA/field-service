# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class FSMPerson(TransactionCase):
    def setUp(self):
        super(FSMPerson, self).setUp()
        self.Worker = self.env["fsm.person"]

    def test_fsm_person(self):
        """Test creating new person
        - Default stage
        - Change stage
        - _search
        - archive the person
        """
        # Create a person
        view_id = "fieldservice.fsm_person_form"
        with Form(self.Worker, view=view_id) as f:
            f.name = "Worker A"
        worker = f.save()
        # Test initial stage
        self.assertEqual(worker.stage_id, self.env.ref("fieldservice.worker_stage_1"))
        # Test change state
        worker.next_stage()
        self.assertEqual(worker.stage_id, self.env.ref("fieldservice.worker_stage_2"))
        worker.next_stage()
        self.assertEqual(worker.stage_id, self.env.ref("fieldservice.worker_stage_3"))
        self.assertTrue(worker.hide)  # hide as max stage
        worker.previous_stage()
        self.assertEqual(worker.stage_id, self.env.ref("fieldservice.worker_stage_2"))
        # Test search
        # TODO: https://github.com/OCA/field-service/issues/265
        # Test archive
        worker.toggle_active()
        self.assertEqual(worker.active, False)
        self.assertEqual(worker.active_partner, True)
