from odoo import fields, models


class RejectProposal(models.Model):
    _name = 'reject.proposal.wiz'

    reject_reason = fields.Text(string="Reason")

    def reject_operation(self):
        """Rejects the proposal assigned to the employee.
        This wizard can also be used with work order as well."""
        model = self._context.get('active_model')
        workset_obj = self.env['fsm.work_set']
        if model == 'fsm.work_set':
            rec = \
                workset_obj.browse(self._context.get('default_id'))
            if rec:
                rec.reject_reason = self.reject_reason
                rec.reject_operation()
        return False
