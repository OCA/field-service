# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFSMVehicleTranslation(TransactionCase):
    def test_vehicle_name_is_translatable(self):
        self.assertTrue(self.env["fsm.vehicle"]._fields["name"].translate)
