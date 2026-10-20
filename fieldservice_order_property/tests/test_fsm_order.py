# Copyright 2024 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestFSMOrder(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.team_a = cls.env.ref("fieldservice.fsm_team_default")
        properties_def = [
            {"name": "date", "type": "date", "string": "Date", "default": "2026-01-01"},
            {
                "name": "integer",
                "type": "integer",
                "string": "ID",
                "default": 1,
            },
        ]
        cls.team_a.fsm_order_properties_definition = properties_def
        cls.team_b = cls.env["fsm.team"].create({"name": "Team B"})
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.fsm_order_team_a = cls.env["fsm.order"].create(
            {
                "name": "Test Order Team A",
                "team_id": cls.team_a.id,
                "location_id": cls.test_location.id,
            }
        )

    def test_fsm_order_properties_within_team(self):
        self.fsm_order_team_a.fsm_order_properties = {
            "date": "2026-01-03",
            "integer": 5,
        }

        properties = self.fsm_order_team_a.fsm_order_properties
        self.assertEqual(len(properties), 2)
        self.assertFalse(self.team_b.fsm_order_properties_definition)

    def test_fsm_order_properties_read_group(self):
        self.fsm_order_team_a.fsm_order_properties = {"date": "2026-01-03"}
        groups = self.env["fsm.order"].read_group(
            domain=[("id", "=", self.fsm_order_team_a.id)],
            fields=["fsm_order_properties.date"],
            groupby=["fsm_order_properties.date:day"],
        )
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["fsm_order_properties.date_count"], 1)

    def test_search_view_groups_by_property(self):
        view = self.env.ref("fieldservice_order_property.fsm_order_search_view")
        self.assertIn('name="fsm_order_properties"', view.arch_db)
        self.assertNotIn("group_by_fsm_order_properties", view.arch_db)
