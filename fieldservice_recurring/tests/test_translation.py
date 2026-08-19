# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFSMRecurringTranslation(TransactionCase):
    def test_configuration_fields_are_translatable(self):
        fields_by_model = {
            "fsm.recurring.template": ("name", "description"),
            "fsm.frequency": ("name",),
            "fsm.frequency.set": ("name",),
        }
        for model_name, field_names in fields_by_model.items():
            for field_name in field_names:
                self.assertTrue(
                    self.env[model_name]._fields[field_name].translate,
                    f"{model_name}.{field_name} must be translatable",
                )
