# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from odoo.addons.fieldservice_timeline import hooks


class FSMUninstall(TransactionCase):
    def test_fsm_uninstall(self):
        hooks.uninstall_hook(self.env.cr, False)
