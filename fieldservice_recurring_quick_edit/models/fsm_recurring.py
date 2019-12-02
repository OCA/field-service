# Copyright (C) 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta
from dateutil.rrule import rruleset

from odoo import _, api, fields, models

from odoo.addons.fieldservice_recurring_quick_edit.models.fsm_frequency import WEEKDAYS_SELECT


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"
    _inherits = {'fsm.frequency.set': 'fsm_frequency_set_qedit_id'}

    name = fields.Char(
        related='fsm_frequency_set_qedit_id.name', inherited=True, readonly=False
    )
    fsm_frequency_set_id = fields.Many2one(required=False)
    fsm_frequency_set_qedit_id = fields.Many2one("fsm.frequency.set",
            required=True, ondelete='restrict', auto_join=True,
            string='Quick Edit Frequency Set',
            help='Quick Edit Frequency Set-related data to the user Recurring Order')
    frequency_type = fields.Selection(
        [
            ("use_predefined", "Use predifined frequency"),
            ("edit_inplace", "Quick edit"),
        ],
        default="use_predefined",
    )
    fsm_frequency_ids = fields.Many2many(related='fsm_frequency_set_qedit_id.fsm_frequency_ids', readonly=False, string="Frequency Rules")

    @api.onchange("frequency_type ")
    def _onchange_frequency_type(self):
        for fsmr in self:
            if fsmr.frequency_type == "edit_inplace":
                fmsr.fsm_frequency_set_id = False

    @api.model_cr
    def init(self):
        # set all existing unset fsm_frequency_set_qedit_id fields to ``true``
        self._cr.execute('UPDATE fsm_recurring'
                         ' SET fsm_frequency_set_qedit_id = fsm_frequency_set_id'
                         ' WHERE fsm_frequency_set_qedit_id IS NULL')

    def _update_frequency_set(self):
        if self.frequency_type == 'edit_inplace':
            vals["fsm_frequency_set_id"] =  vals.get("fsm_frequency_set_qedit_id")
        return vals

    @api.model
    def create(self, vals):
        import pdb; pdb.set_trace()
        res = super(FSMRecurringOrder, self).create(vals)
        if res.frequency_type == 'edit_inplace':
            res.fsm_frequency_set_id = res.fsm_frequency_set_qedit_id
        return res
# 
    # @api.model
    # def create(self, vals):
        # self._update_frequency_set(vals)
        # return super(FSMRecurringOrder, self).create(vals)
