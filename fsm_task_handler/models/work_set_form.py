from odoo import api, fields, models


class WorkSetForms(models.Model):
    _name = 'work_set.form'

    name = fields.Many2one('product.survey',
                           string="Questionnaires",
                           required=True)
    work_set_id = fields.Many2one('fsm.work_set')

    @api.onchange('work_set_id')
    def onchange_workset(self):
        """Filtering the surveys based on the selected customer.
        If the customer owns some products, then we will
        check the questionnaire category of that product
         and shows only those questionnaires in that category.
        If the customer doesnot own any product, we will
         show all the questionnaires."""
        categ_ids = self.work_set_id.question_categ.ids
        return {
            'domain': {
                'name': [
                    ('question_categ', 'in', categ_ids)
                ] if categ_ids else []
            }
        }

    @api.multi
    def action_test_survey(self):
        """
        Returns a tree view where we can answer the questions
        related to the current work-set and survey.
        """
        tree_id = 'fsm_task_handler.product_survey_answer_editable_tree'
        view = self.env.ref(tree_id)
        return {
            'name': 'Answers',
            'type': 'ir.actions.act_window',
            'res_model': 'work_set.answers',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view.id,
            'domain': [
                ('work_set_id', '=', self.work_set_id.id),
                ('survey_id', '=', self.name.id)
            ]
        }

    @api.multi
    def action_result_survey(self):
        """
        Returns all the questions & answers related to
        that survey(Non-editable, just for view).
        """
        view = self.env.ref('fsm_task_handler.product_survey_answer_tree')
        return {
            'name': 'Answers',
            'type': 'ir.actions.act_window',
            'res_model': 'work_set.answers',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': view.id,
            'domain': [
                ('work_set_id', '=', self.work_set_id.id),
                ('survey_id', '=', self.name.id)
            ]
        }


class QuestionnaireCateg(models.Model):
    _name = 'question.category'

    name = fields.Char(string="Name")
    work_set_id = fields.Many2one('fsm.work_set')
    product_id = fields.Many2one('product.product')


class WorkSetAnswers(models.Model):
    _name = 'work_set.answers'

    name = fields.Char(string="question", readonly=True)
    answer = fields.Char(string="Answer")
    survey_id = fields.Many2one('product.survey', string="Survey")
    work_set_id = fields.Many2one('fsm.work_set', string="Workset")


class ProductSurveys(models.Model):
    _name = 'product.survey'

    name = fields.Char(string="Question")
    questionnaire = fields.One2many('product.questionnaire', 'survey_id',
                                    string="Questionnaires", required=True)
    question_categ = fields.Many2one('question.category',
                                     string="Questionnaire Category",
                                     required=True)


class ProductQuestionnaires(models.Model):
    _name = 'product.questionnaire'

    name = fields.Char(string="Question")
    survey_id = fields.Many2one('product.survey')
