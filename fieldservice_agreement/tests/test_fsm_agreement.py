# Copyright (C) 2019 - TODAY, Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, fields

from odoo.addons.fieldservice.tests.test_fsm_common import FSMCommon


class FSMOrder(FSMCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Order = cls.env["fsm.order"]
        cls.Agreement = cls.env["agreement"]
        cls.Equipment = cls.env["fsm.equipment"]
        cls.agreement_type = cls.env["agreement.type"].create(
            {"name": "Test Agreement Type"}
        )

    def test_fsm_agreement(self):
        """
        By create new order and equipment and link to an agreement, I expect,
        - Agreement count and link to the order/equipment is corrrect
        - Location's service profile display correctly
        - Person (partner) can relate back to agreement correctly
        """
        # Create agreement and assign to test location
        agreement = self.Agreement.create(
            {
                "name": "Test Agreement",
                "agreement_type_id": self.agreement_type.id,
                "code": "TestAgreement",
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
                "fsm_location_ids": [Command.set([self.test_location.id])],
                "partner_id": self.test_person.partner_id.id,
            }
        )
        # Create 2 Orders, that link to this agreement
        vals = {
            "name": "Order1",
            "location_id": self.test_location.id,
            "agreement_id": agreement.id,
        }
        order1 = self.Order.create(vals)
        agreement._compute_service_order_count()
        self.assertEqual(agreement.service_order_count, 1)
        self.assertEqual(order1.id, agreement.action_view_service_order()["res_id"])
        vals = {
            "name": "Order2",
            "location_id": self.test_location.id,
            "agreement_id": agreement.id,
        }
        order2 = self.Order.create(vals)
        agreement._compute_service_order_count()
        self.assertEqual(agreement.service_order_count, 2)
        self.assertEqual(
            [order1.id, order2.id],
            agreement.action_view_service_order()["domain"][0][2],
        )
        # Create 3 equipment, that link to this agreement
        vals = {
            "name": "EQ1",
            "current_location_id": self.test_location.id,
            "agreement_id": agreement.id,
        }
        equipment1 = self.Equipment.create(vals)
        agreement._compute_service_order_count()
        self.assertEqual(agreement.equipment_count, 1)
        self.assertEqual(equipment1.id, agreement.action_view_fsm_equipment()["res_id"])
        equipment2 = equipment1.copy({"name": "EQ2"})
        equipment3 = equipment1.copy({"name": "EQ3"})
        agreement._compute_equipment_count()
        self.assertEqual(agreement.equipment_count, 3)
        self.assertEqual(
            [equipment1.id, equipment2.id, equipment3.id],
            agreement.action_view_fsm_equipment()["domain"][0][2],
        )
        # Person (partner) can relate back to agreement correctly
        self.assertEqual(self.test_person.agreement_count, 1)
        self.assertEqual(
            self.test_person.action_view_agreements()["res_id"], agreement.id
        )
        # With a second agreement on the same partner, the action returns a
        # domain covering all matching agreements instead of a single record
        agreement2 = self.Agreement.create(
            {
                "name": "Test Agreement 2",
                "agreement_type_id": self.agreement_type.id,
                "code": "TestAgreement2",
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
                "fsm_location_ids": [Command.set([self.test_location.id])],
                "partner_id": self.test_person.partner_id.id,
            }
        )
        self.test_person.invalidate_recordset(["agreement_count"])
        self.assertEqual(self.test_person.agreement_count, 2)
        self.assertEqual(
            sorted(self.test_person.action_view_agreements()["domain"][0][2]),
            sorted([agreement.id, agreement2.id]),
        )
