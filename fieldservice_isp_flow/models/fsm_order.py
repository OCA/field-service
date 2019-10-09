# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, _
from odoo.exceptions import ValidationError


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    def action_confirm(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice_isp_flow.fsm_stage_confirmed').id})

    def action_request(self):
        if not self.person_ids:
            raise ValidationError(_("Cannot move to Requested " +
                                    "until 'Request Workers' is filled in"))
        return self.write({'stage_id': self.env.ref(
            'fieldservice_isp_flow.fsm_stage_requested').id})

    def action_assign(self):
        if self.person_id:
            return self.write({'stage_id': self.env.ref(
                'fieldservice_isp_flow.fsm_stage_assigned').id})
        else:
            raise ValidationError(_("Cannot move to Assigned " +
                                    "until 'Assigned To' is filled in"))

    def action_schedule(self):
        if self.scheduled_date_start and self.person_id:
            return self.write({'stage_id': self.env.ref(
                'fieldservice_isp_flow.fsm_stage_scheduled').id})
        else:
            raise ValidationError(_("Cannot move to Scheduled " +
                                    "until both 'Assigned To' and " +
                                    "'Scheduled Start Date' are filled in"))

    def action_enroute(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice_isp_flow.fsm_stage_enroute').id})

    def action_start(self):
        if not self.date_start:
            raise ValidationError(_("Cannot move to Start " +
                                    "until 'Actual Start' is filled in"))
        return self.write({'stage_id': self.env.ref(
            'fieldservice_isp_flow.fsm_stage_started').id})

    def action_complete(self):
        if not self.date_end:
            raise ValidationError(_("Cannot move to Complete " +
                                    "until 'Actual End' is filled in"))
        if not self.resolution:
            raise ValidationError(_("Cannot move to Complete " +
                                    "until 'Resolution' is filled in"))
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_completed').id})

    def action_cancel(self):
        return self.write({'stage_id': self.env.ref(
            'fieldservice.fsm_stage_cancelled').id})
