# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EmployeeAvailability(models.Model):
    _inherit = 'fsm.person'

    available = fields.Boolean(
            string="Availability",
            default=True,
            help="Shows status of the person."
                 "This status will be updated "
                 "when person is started/finished "
                 "a job."
    )
    # skill sets of this person
    skill_ids = fields.Many2many(
            'fsm.skills',
            'person_skills_rel',
            'person_id',
            'skill_id',
            string="Basic Skills"
    )


class ResPartnerPerson(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def write(self, vals):
        """Making the person-partner relation bidirectional.
        In case we need to link the user with a person,
         we can enable the flag 'Is a FS Person' and
         a new person will be created and linked with this partner.
        """
        res = super(ResPartnerPerson, self).write(vals)
        # checking for the flag
        if 'fsm_person' in vals \
                and vals['fsm_person'] == True:
            if self.env['fsm.person'].search([('partner_id', '=', self.id)]):
                # a person exists for this partner, so doing nothing
                return res
            else:
                # creating a new person
                self._cr.execute("INSERT INTO fsm_person (partner_id) "
                                 "VALUES(%s)",
                                 (self.id, ))
                return res
