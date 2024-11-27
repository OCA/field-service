# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# @author: Italo Lopes <italo.lopes@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestRepairPartSourceLocation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order_type = cls.env.ref("fieldservice_repair.fsm_order_type_repair")
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.stock_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {"name": "Product A", "type": "product"}
        )
        cls.lot = cls.env["stock.lot"].create(
            {
                "name": "sn11",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product.id,
                "location_id": cls.stock_location.id,
                "quantity": 1.0,
                "lot_id": cls.lot.id,
            }
        )
        cls.equipment = cls.env["fsm.equipment"].create(
            {
                "name": "test equipment",
                "product_id": cls.product.id,
                "lot_id": cls.lot.id,
            }
        )
        cls.agreement = cls.env["agreement"].create(
            {
                "name": "Test Agreement",
                "code": "TestAgreement",
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
            }
        )

    def _prepare_fsm_order_vals(self):
        return {
            "type": self.order_type.id,
            "location_id": self.test_location.id,
            "equipment_id": self.equipment.id,
            "date_start": fields.Datetime.today(),
            "date_end": fields.Datetime.today() + timedelta(hours=1),
            "request_early": fields.Datetime.today(),
        }

    def test_agreement_propagated_from_fsm_order(self):
        fsm_order_vals = self._prepare_fsm_order_vals()
        fsm_order_vals["agreement_id"] = self.agreement.id
        fsm_order = self.env["fsm.order"].create(fsm_order_vals)
        self.assertEqual(fsm_order.repair_id.agreement_id.id, self.agreement.id)

    def test_agreement_propagated_from_equipment(self):
        self.equipment.agreement_id = self.agreement
        fsm_order_vals = self._prepare_fsm_order_vals()
        fsm_order = self.env["fsm.order"].create(fsm_order_vals)
        self.assertEqual(fsm_order.repair_id.agreement_id.id, self.agreement.id)

    def test_agreement_propagated_from_equipment_takes_precedence(self):
        # Equipment uses agreement 02
        agreement_2 = self.agreement.copy({"name": "Test Agreement 2"})
        self.equipment.agreement_id = agreement_2
        # Order uses original agreement
        fsm_order_vals = self._prepare_fsm_order_vals()
        fsm_order_vals["agreement_id"] = agreement_2.id
        fsm_order = self.env["fsm.order"].create(fsm_order_vals)
        # Repair order should use the equipment agreement
        self.assertEqual(fsm_order.repair_id.agreement_id.id, agreement_2.id)

    def test_no_agreement(self):
        fsm_order_vals = self._prepare_fsm_order_vals()
        fsm_order = self.env["fsm.order"].create(fsm_order_vals)
        self.assertFalse(fsm_order.repair_id.agreement_id)
