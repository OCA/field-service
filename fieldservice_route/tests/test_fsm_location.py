# Copyright (C) 2026 Gray Matter Logic
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class TestFSMLocationRoute(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.route = cls.env["fsm.route"].create(
            {
                "name": "Location Route",
                "max_order": 3,
                "fsm_person_id": cls.test_person.id,
                "day_ids": [
                    (6, 0, [cls.env.ref("fieldservice_route.fsm_route_day_0").id])
                ],
            }
        )

    def test_location_route_field(self):
        self.test_location.fsm_route_id = self.route
        self.assertEqual(self.test_location.fsm_route_id, self.route)

    def test_stage_route_type(self):
        stage = self.env["fsm.stage"].create(
            {
                "name": "Route Stage",
                "stage_type": "route",
                "sequence": 99,
            }
        )
        self.assertEqual(stage.stage_type, "route")
