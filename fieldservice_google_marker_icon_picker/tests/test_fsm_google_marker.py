# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


from odoo.tests.common import TransactionCase


class FSMGoogleMarkerCase(TransactionCase):
    def setUp(self):
        super(FSMGoogleMarkerCase, self).setUp()
        self.fsm_stage = self.env.ref("fieldservice.equipment_stage_1")

    def test_location_wiz(self):
        self.fsm_stage.choose_color = "red"
        self.fsm_stage._onchange_choose_color()
