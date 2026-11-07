# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase, new_test_user


class TestFSMOrderEquipmentLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipments = cls.env["fsm.equipment"].create(
            [{"name": "Equipment 1"}, {"name": "Equipment 2"}]
        )
        cls.order = cls.env["fsm.order"].create(
            {
                "location_id": cls.env.ref("fieldservice.test_location").id,
                "equipment_line_ids": [
                    (0, 0, {"equipment_id": equipment.id})
                    for equipment in cls.equipments
                ],
            }
        )
        cls.line = cls.order.equipment_line_ids[0]

    def test_lines_sync_order_equipments(self):
        self.assertEqual(self.order.equipment_ids, self.equipments)
        # an equipment can be listed more than once: it leaves with its last line
        again = self.line.copy()
        self.line.unlink()
        self.assertEqual(self.order.equipment_ids, self.equipments)
        again.unlink()
        self.assertEqual(self.order.equipment_ids, self.equipments[1])

    def test_line_states(self):
        self.assertEqual(self.order.equipment_line_pending_count, 2)
        self.line.action_done()
        self.assertEqual(self.line.state, "done")
        self.assertTrue(self.line.date_done)
        self.assertEqual(self.order.equipment_line_pending_count, 1)
        self.line.action_not_found()
        self.assertEqual(self.line.state, "not_found")
        self.assertFalse(self.line.date_done)
        self.line.action_pending()
        self.assertEqual(self.order.equipment_line_pending_count, 2)

    def test_technician_manages_lines(self):
        technician = new_test_user(
            self.env, login="technician", groups="fieldservice.group_fsm_user_own"
        )
        Line = self.env["fsm.order.equipment.line"].with_user(technician)
        for operation in ("read", "write", "create", "unlink"):
            Line.check_access(operation)
