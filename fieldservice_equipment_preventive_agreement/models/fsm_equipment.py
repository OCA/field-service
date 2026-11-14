# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMEquipmentPreventive(models.Model):
    _inherit = "fsm.equipment.preventive"

    agreement_rule_id = fields.Many2one(
        "agreement.preventive.rule",
        string="Agreement Rule",
        ondelete="set null",
        readonly=True,
        help="Rule of the agreement that manages this visit.",
    )
    from_agreement = fields.Boolean(readonly=True)


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    @api.model_create_multi
    def create(self, vals_list):
        equipments = super().create(vals_list)
        equipments._sync_agreement_preventives()
        return equipments

    def write(self, vals):
        res = super().write(vals)
        if "agreement_id" in vals:
            self._sync_agreement_preventives()
        return res

    def _sync_agreement_preventives(self):
        """Preventive visits of the equipment given by the rules of its agreement.

        Visits added by hand are left alone; the dates of the visits already
        registered are kept when only the interval changes.
        """
        Preventive = self.env["fsm.equipment.preventive"].sudo()
        to_create = []
        for equipment in self.sudo():
            wanted = {}
            for rule in equipment.agreement_id.preventive_rule_ids:
                if rule.type_id not in wanted and rule._matches(equipment):
                    wanted[rule.type_id] = rule
            for preventive in equipment.preventive_ids:
                rule = wanted.pop(preventive.type_id, None)
                if rule:
                    preventive.write(
                        {
                            "interval": rule.interval,
                            "template_id": rule._get_template(equipment).id,
                            "agreement_rule_id": rule.id,
                            "from_agreement": True,
                        }
                    )
                elif preventive.from_agreement:
                    preventive.unlink()
            to_create += [
                {
                    "equipment_id": equipment.id,
                    "type_id": visit_type.id,
                    "interval": rule.interval,
                    "template_id": rule._get_template(equipment).id,
                    "agreement_rule_id": rule.id,
                    "from_agreement": True,
                }
                for visit_type, rule in wanted.items()
            ]
        Preventive.create(to_create)
