# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestFSMAvailabilityTranslation(TransactionCase):
    def test_blackout_group_name_is_translatable(self):
        self.assertTrue(self.env["fsm.blackout.group"]._fields["name"].translate)
