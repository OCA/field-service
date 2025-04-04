# Copyright 2025 Bernat Obrador APSL-Nagarro (bobrador@apsl.net).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import requests

from odoo.tests import tagged

from odoo.addons.point_of_sale.tests.test_frontend import TestPointOfSaleHttpCommon


@tagged("post_install", "-at_install")
class CommonFsOrderFromPos(TestPointOfSaleHttpCommon):
    @classmethod
    def setUpClass(cls):
        cls._super_send = requests.Session.send
        super().setUpClass()
        cls.white_board_product = cls.env["product.product"].search(
            [("name", "ilike", "Whiteboard Pen")], limit=1
        )
        cls.wall_shelf_unit = cls.env["product.product"].search(
            [("name", "ilike", "Wall Shelf Unit")], limit=1
        )

        cls.white_board_product.field_service_tracking = "sale"
        cls.stage = cls.env["fsm.stage"].create(
            {"name": "Test Stage", "stage_type": "order", "is_default": True}
        )
        cls.team = cls.env["fsm.team"].create({"name": "Team test"})
        cls.config = cls.env["pos.config"].search(
            [("company_id", "=", cls.env.company.id)]
        )
        cls.new_stage = cls.env.ref("fieldservice.fsm_stage_new")
        cls.completed_stage = cls.env.ref("fieldservice.fsm_stage_completed")
        cls.cancelled_stage = cls.env.ref("fieldservice.fsm_stage_cancelled")

        cls.env.ref("fieldservice.fsm_team_default").sudo().write({"stage_ids": False})
        cls.new_stage.sudo().write({"company_id": False})
        cls.completed_stage.sudo().write({"company_id": False})
        cls.cancelled_stage.sudo().write({"company_id": False})

        # Adds compatibility for isp_flow module
        if (
            cls.env["ir.module.module"]
            .sudo()
            .search_count(
                [("name", "=", "fieldservice_isp_flow"), ("state", "=", "installed")]
            )
        ):
            cls.env.ref("fieldservice_isp_flow.fsm_stage_confirmed").sudo().write(
                {"company_id": False}
            )
            cls.env.ref("fieldservice_isp_flow.fsm_stage_requested").sudo().write(
                {"company_id": False}
            )
            cls.env.ref("fieldservice_isp_flow.fsm_stage_assigned").sudo().write(
                {"company_id": False}
            )
            cls.env.ref("fieldservice_isp_flow.fsm_stage_scheduled").sudo().write(
                {"company_id": False}
            )
            cls.env.ref("fieldservice_isp_flow.fsm_stage_enroute").sudo().write(
                {"company_id": False}
            )
            cls.env.ref("fieldservice_isp_flow.fsm_stage_started").sudo().write(
                {"company_id": False}
            )
        cls.partner_1 = cls.env["res.partner"].search(
            [("name", "ilike", "Addison Olson")], limit=1
        )
        cls.env["fsm.wizard"].action_convert_location(cls.partner_1)
        # Adds compatibility for fieldservice_account_analytic module
        if (
            cls.env["ir.module.module"]
            .sudo()
            .search_count(
                [
                    ("name", "=", "fieldservice_account_analytic"),
                    ("state", "=", "installed"),
                ]
            )
        ):
            cls.analytic_plan = cls.env["account.analytic.plan"].create(
                {"name": "Test Plan"}
            )
            fsm_location = cls.env["fsm.location"].search(
                [("partner_id", "=", cls.partner_1.id)]
            )
            fsm_location.analytic_account_id = cls.env[
                "account.analytic.account"
            ].create(
                {
                    "name": cls.partner_1.name,
                    "partner_id": cls.partner_1.id,
                    "company_id": cls.env.company.id,
                    "plan_id": cls.analytic_plan.id,
                }
            )

    # Needed to avoid conflicts with fieldservice_geoengine when it's installed
    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        """Don't block external requests."""
        return cls._super_send(s, r, **kw)

    def _start_tour(self, tour_name, login=None):
        self.config.open_ui()
        self.start_tour(
            f"/pos/ui?config_id={self.config.id}",
            tour_name,
            login=login,
        )
