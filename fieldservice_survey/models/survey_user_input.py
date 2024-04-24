# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveyUserInput(models.Model):

    _inherit = "survey.user_input"

    fsm_order_id = fields.Many2one("fsm.order", string="FSM Order")
    fsm_order_person_id = fields.Many2one("fsm.person", "FSM Order Person ")
