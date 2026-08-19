# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestFSMActivityTranslation(TransactionCase):
    def test_activity_name_is_translatable(self):
        self.assertTrue(self.env["fsm.activity"]._fields["name"].translate)
