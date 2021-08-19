# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockPutawayRule(TransactionCase):
    def setUp(self):
        super(TestStockPutawayRule, self).setUp()

        self.StockPutawayRule = self.env["stock.putaway.rule"]

        currency = self.env["res.currency"].create(
            {
                "name": "Currency 1",
                "symbol": "$",
            }
        )
        partner = self.env["res.partner"].create(
            {
                "name": "Partner 1",
            }
        )
        self.company1 = self.env["res.company"].create(
            {
                "name": "Company 1",
                "currency_id": currency.id,
                "partner_id": partner.id,
            }
        )
        self.location_in = self.env["stock.location"].create(
            {
                "name": "Location In",
                "usage": "internal",
                "company_id": self.company1.id,
            }
        )
        self.location_out = self.env["stock.location"].create(
            {
                "name": "Location Out",
                "usage": "internal",
                "company_id": self.company1.id,
            }
        )
        self.vehicle_location = self.env["stock.location"].create(
            {
                "name": "Vehicle Location",
                "usage": "internal",
                "company_id": self.company1.id,
            }
        )
        self.vehicle_id = self.env["fsm.vehicle"].create(
            {
                "name": "Vehicle 1",
                "inventory_location_id": self.vehicle_location.id,
            }
        )
        self.stock_putaway_rule = self.StockPutawayRule.create(
            {
                "company_id": self.company1.id,
                "location_in_id": self.location_in.id,
                "location_out_id": self.location_out.id,
                "method": "fixed",
            }
        )

    def test_get_putaway_options(self):
        res = self.stock_putaway_rule._get_putaway_options()

        self.assertEqual(res[0][0], "fixed")
        self.assertEqual(res[0][1], "Fixed Location")
        self.assertEqual(res[1][0], "vehicle")
        self.assertEqual(res[1][1], "Location of the vehicle")

    def test_get_vehicle_location(self):
        res = self.stock_putaway_rule.get_vehicle_location()
        self.assertEqual(res, self.env["stock.location"])

        res = self.stock_putaway_rule.with_context(
            {"vehicle_id": self.vehicle_id.id}
        ).get_vehicle_location()
        self.assertEqual(res, self.vehicle_location)
