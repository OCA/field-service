from odoo import fields, models


class FsmOrder(models.Model):
    _inherit = "fsm.order"

    partner_submitted_answer_survey_ids = fields.Many2many(
        "res.partner", string="Submitted Survey"
    )

    def action_submit_fsm_order_survey(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "fsm.order.survey.submit",
            "target": "new",
            "name": "Submit Survey ",
        }

    def action_open_survey_inputs(self):
        return {
            "type": "ir.actions.act_url",
            "name": "Survey Answer",
            "target": "self",
            "url": "/fsm_order/%s/results/" % self.id,
        }
