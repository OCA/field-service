# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    has_stage_changed = fields.Boolean(default=False)
    next_request_assign = fields.\
        Datetime(string="Next Request Assigned Worker for ETA Date")

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            vals.update({'has_stage_changed': True})
        else:
            vals.update({'has_stage_changed': False})
        return super(FSMOrder, self).write(vals)

    def check_time(self):
        time_now = datetime.now().time()
        if time_now < datetime.time(18,00) and time_now > datetime.time(9,00):
            return True
        else:
            return False

    def update_next_request(self):
        if self.priority == 0:
            self.next_request_assign = datetime.now() + timedelta(hours=24)
        elif self.priority == 1:
            self.next_request_assign = datetime.now() + timedelta(hours=8)
        elif self.priority == 2:
            self.next_request_assign = datetime.now() + timedelta(hours=2)
        else:
            self.next_request_assign = datetime.now() + timedelta(hours=1)

