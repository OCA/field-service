# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFSMSizeTranslation(TransactionCase):
    def test_size_name_is_translatable(self):
        self.assertTrue(self.env["fsm.size"]._fields["name"].translate)
