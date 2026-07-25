# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.fieldservice_timeline import hooks


class FSMUninstall(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def test_fsm_uninstall(self):
        # Action with timeline in the middle of view_mode
        action_mid = self.env["ir.actions.act_window"].create(
            {
                "name": "Timeline Mid",
                "res_model": "fsm.order",
                "view_mode": "list,timeline,form",
            }
        )
        # Action with timeline at the start of view_mode
        action_start = self.env["ir.actions.act_window"].create(
            {
                "name": "Timeline Start",
                "res_model": "fsm.order",
                "view_mode": "timeline,list,form",
            }
        )
        # Action without timeline (should stay unchanged)
        action_plain = self.env["ir.actions.act_window"].create(
            {
                "name": "No Timeline",
                "res_model": "fsm.order",
                "view_mode": "list,form",
            }
        )
        hooks.uninstall_hook(self.env)
        self.assertEqual(action_mid.view_mode, "list,form")
        self.assertEqual(action_start.view_mode, "list,form")
        self.assertEqual(action_plain.view_mode, "list,form")
