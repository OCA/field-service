from odoo import models, fields, api


# model for stages
class StagesFSM(models.Model):
    _name = 'fsm.stages'

    sequence = fields.Integer()
    name = fields.Char(string="Stage Name",
                       required=True
                       )
    fold = fields.Boolean(default=True,
                          string="Folded in Kanban"
                          )
    ref_name = fields.Char(string="Reference",
                           help="We can use this value to refer this stage."
                           )
    ref_editable = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        res = super(StagesFSM, self).create(vals)
        # we are creating a constant value which can be used
        # to access this stage
        # this value will be editable only at the time of creation.
        # we are setting a flag(field) to make the reference field readonly

        # if something is provided in the reference section, we will
        # convert it to lowercase and append this stage's id to it
        if vals.get('ref_name'):
            ref_name = vals.get('ref_name').lower()
            ref_name = ref_name.replace(' ', '_')
        else:
            ref_name = res.name.lower()
            ref_name = ref_name.replace(' ', '_')
        res.ref_name = ref_name + '_' + str(res.id)
        # disabling the flag to make the field readonly
        res.ref_editable = False
        return res

    @api.multi
    def write(self, vals):
        res = super(StagesFSM, self).write(vals)
        # just to make sure that the flag is disabled
        # (to make the reference readonly)
        if self.ref_editable:
            self.ref_editable = False
        return res
