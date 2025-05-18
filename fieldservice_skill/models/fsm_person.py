# Copyright (C) 2018, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMPerson(models.Model):
    _inherit = "fsm.person"

    skill_ids = fields.One2many("fsm.person.skill", "person_id", string="Skills")
