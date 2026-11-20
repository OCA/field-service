# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError, UserError
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

    def test_unlink_keeps_equipment_added_on_order(self):
        direct = self.env["fsm.equipment"].create({"name": "Direct"})
        self.order.equipment_ids = [(4, direct.id)]
        self.line.unlink()
        self.assertEqual(self.order.equipment_ids, self.equipments[1] | direct)

    def test_change_line_equipment_syncs_order(self):
        other = self.env["fsm.equipment"].create({"name": "Equipment 3"})
        self.line.equipment_id = other
        self.assertEqual(self.order.equipment_ids, self.equipments[1] | other)
        # still listed by another line: the previous equipment stays
        self.order.equipment_line_ids[1].equipment_id = other
        self.assertEqual(self.order.equipment_ids, other)
        self.line.note = "checked"
        self.assertEqual(self.order.equipment_ids, other)

    def test_unlink_order_with_lines(self):
        lines = self.order.equipment_line_ids
        self.order.unlink()
        self.assertFalse(lines.exists())

    def test_multi_company(self):
        company = self.env["res.company"].create({"name": "Other Company"})
        foreign = self.env["fsm.equipment"].create(
            {"name": "Foreign", "company_id": company.id}
        )
        with self.assertRaises(UserError):
            self.line.equipment_id = foreign
        location = self.env["fsm.location"].create(
            {
                "name": "Foreign Location",
                "owner_id": self.env["res.partner"].create({"name": "Owner"}).id,
                "company_id": company.id,
            }
        )
        foreign_order = self.env["fsm.order"].create(
            {
                "location_id": location.id,
                "company_id": company.id,
                "stage_id": self.order.stage_id.id,
                "equipment_line_ids": [(0, 0, {"equipment_id": foreign.id})],
            }
        )
        user = new_test_user(
            self.env,
            login="dispatcher",
            groups="fieldservice.group_fsm_dispatcher",
            company_id=self.env.company.id,
            company_ids=[(6, 0, self.env.company.ids)],
        )
        foreign_line = foreign_order.equipment_line_ids
        self.assertEqual(foreign_line.company_id, company)
        Line = self.env["fsm.order.equipment.line"].with_user(user)
        self.assertFalse(Line.search([("id", "=", foreign_line.id)]))
        with self.assertRaises(AccessError):
            foreign_line.with_user(user).read(["state"])
