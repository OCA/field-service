# Copyright (C) 2020, Brian McMaster
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SavepointCase


class TestFSMStockCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestFSMStockCommon, cls).setUpClass()

        cls.ModelData = cls.env["ir.model.data"]
        cls.FSMOrder = cls.env["fsm.order"]
        cls.Product = cls.env["product.product"]

        cls.stock_cust_loc = cls.ModelData.xmlid_to_res_id(
            "stock.stock_location_customers")
        cls.partner_1 = cls.env["res.partner"].with_context(
            tracking_disable=True).create({"name": "Partner 1"})
        cls.fsm_location_1 = cls.env["fsm.location"].create({
            "name": "FSM Location 1",
            "owner_id": cls.partner_1.id,
            "customer_id": cls.partner_1.id,
            "inventory_location_id": cls.stock_cust_loc,
        })
