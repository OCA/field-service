# Copyright (C) 2019 - TODAY, mourad EL HADJ MIMOUNE, Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"
    _inherits = {'fsm.frequency.set': 'fsm_frequency_set_qedit_id'}

    name = fields.Char(
        related='fsm_frequency_set_qedit_id.name',
        inherited=True, readonly=False
    )
    fsm_frequency_set_id = fields.Many2one(required=False)
    fsm_frequency_set_qedit_id = fields.Many2one(
        "fsm.frequency.set",
        required=True, ondelete='restrict', auto_join=True,
        string='Quick Edit Frequency Set',
        help='Quick Edit Frequency Set-related '
        'data to the user Recurring Order')
    frequency_type = fields.Selection(
        [
            ("use_predefined", "Use predifined frequency"),
            ("edit_inplace", "Quick edit"),
        ],
        default="use_predefined",
    )
    fsm_frequency_ids = fields.Many2many(
        related='fsm_frequency_set_qedit_id.fsm_frequency_ids',
        readonly=False, string="Frequency Rules")

    @api.onchange("frequency_type ")
    def _onchange_frequency_type(self):
        for fsmr in self:
            if fsmr.frequency_type == "edit_inplace":
                fsmr.fsm_frequency_set_id = False

    @api.model_cr
    def init(self):
        # set all existing unset fsm_frequency_set_qedit_id fields to ``true``
        self._cr.execute(
             'UPDATE fsm_recurring'
             ' SET fsm_frequency_set_qedit_id = fsm_frequency_set_id'
             ' WHERE fsm_frequency_set_qedit_id IS NULL')
        self._cr.execute(
             'UPDATE fsm_recurring'
             ' SET frequency_type = \'use_predefined\''
             ' WHERE frequency_type IS NULL')

    @api.model
    def create(self, vals):
        res = super(FSMRecurringOrder, self).create(vals)
        if res.frequency_type == 'edit_inplace':
            res.fsm_frequency_set_id = res.fsm_frequency_set_qedit_id
        return res

    @api.multi
    def write(self, vals):
        res = super(FSMRecurringOrder, self).write(vals)
        r_edited = self.filtered(
            lambda r: r.frequency_type == 'edit_inplace'
            and r.fsm_frequency_set_id != r.fsm_frequency_set_qedit_id)
        for re in r_edited:
            re.fsm_frequency_set_id = re.fsm_frequency_set_qedit_id
        return res


    def action_view_fms_order(self):
        fms_orders = self.mapped('fsm_order_ids')
        action = self.env.ref('fieldservice.action_fsm_operation_order').read()[0]
        if len(fms_orders) > 1:
            action['domain'] = [('id', 'in', fms_orders.ids)]
        elif len(fms_orders) == 1:
            form_view = [(self.env.ref('fieldservice.fsm_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = fms_orders.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        action["key2"] = "client_action_multi"
        return action

    @api.multi
    def generate_orders(self):
        """
        Executed from form view (call private method) _generate_orders
        """
        return self._generate_orders()

