# Copyright (C) 2022 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)


from odoo.tests.common import TransactionCase


class FSMLocationBuilderWizardCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fsm_order = cls.env["fsm.order"]
        cls.Wizard = cls.env["fsm.location.builder.wizard"]
        cls.test_location = cls.env.ref("fieldservice.test_location")
        cls.level = cls.env["fsm.location.level"]
        cls.fr = cls.env.ref("base.fr")
        cls.state_fr = cls.env["res.country.state"].create(
            dict(name="State", code="ST", country_id=cls.fr.id)
        )

    def test_location_wiz(self):
        tag = self.env.ref("base.res_partner_category_8")
        self.test_location.write(
            {
                "state_id": self.state_fr.id,
                "country_id": self.fr.id,
                "tz": "Pacific/Honolulu",
            }
        )
        level_1 = self.level.create(
            {
                "name": "Floor",
                "start_number": 2,
                "end_number": 2,
                "spacer": "Test",
                "tag_ids": [(6, 0, tag.ids)],
            }
        )
        level_2 = self.level.create(
            {
                "name": "Room",
                "start_number": 1,
                "end_number": 2,
            }
        )
        level_1._compute_total_number()
        level_2._compute_total_number()
        wiz = self.Wizard.create({"level_ids": [(6, 0, [level_2.id, level_1.id])]})
        wiz.with_context(active_id=self.test_location.id).create_sub_locations()
