# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def action_confirm(self):
        try:
            stage_id = self.env.ref("fieldservice_isp_flow.fsm_stage_confirmed").id
        except (ValueError, KeyError):
            # Fall back to basic write if external ID not available
            stage_id = None
        return self.write({"stage_id": stage_id})

    def action_request(self):
        if not self.person_id and not self.person_ids:
            raise ValidationError(
                _("Cannot move to Requested " + "until 'Assigned To' is filled in")
            )
        try:
            stage_id = self.env.ref("fieldservice_isp_flow.fsm_stage_requested").id
        except (ValueError, KeyError) as e:
            # Fall back to basic write if external ID not available
            _logger.debug("External ID not available for requested stage: %s", e)
            stage_id = None
        return self.write({"stage_id": stage_id})

    def action_assign(self):
        if self.person_id:
            try:
                stage_id = self.env.ref("fieldservice_isp_flow.fsm_stage_assigned").id
            except (ValueError, KeyError):
                # Fall back to basic write if external ID not available
                stage_id = None
            return self.write({"stage_id": stage_id})
        raise ValidationError(
            _("Cannot move to Assigned " + "until 'Assigned To' is filled in")
        )

    def action_schedule(self):
        if self.scheduled_date_start and self.person_id:
            try:
                stage_id = self.env.ref("fieldservice_isp_flow.fsm_stage_scheduled").id
            except (ValueError, KeyError):
                # Fall back to basic write if external ID not available
                stage_id = None
            return self.write({"stage_id": stage_id})
        raise ValidationError(
            _(
                "Cannot move to Scheduled "
                + "until both 'Assigned To' and "
                + "'Scheduled Start Date' are filled in"
            )
        )

    def action_enroute(self):
        try:
            stage_id = self.env.ref("fieldservice_isp_flow.fsm_stage_enroute").id
        except (ValueError, KeyError):
            # Fall back to basic write if external ID not available
            stage_id = None
        return self.write({"stage_id": stage_id})

    def action_start(self):
        if not self.date_start:
            raise ValidationError(
                _("Cannot move to Start " + "until 'Actual Start' is filled in")
            )
        try:
            stage_id = self.env.ref("fieldservice_isp_flow.fsm_stage_started").id
        except (ValueError, KeyError):
            # Fall back to basic write if external ID not available
            stage_id = None
        return self.write({"stage_id": stage_id})

    def action_complete(self):
        if not self.date_end:
            raise ValidationError(
                _("Cannot move to Complete " + "until 'Actual End' is filled in")
            )
        if not self.resolution:
            raise ValidationError(
                _("Cannot move to Complete " + "until 'Resolution' is filled in")
            )
        return super().action_complete()

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "stage_id" in init_values:
            try:
                if (
                    self.stage_id.id
                    == self.env.ref("fieldservice_isp_flow.fsm_stage_confirmed").id
                ):
                    return self.env.ref("fieldservice.mt_order_confirmed")
                if (
                    self.stage_id.id
                    == self.env.ref("fieldservice_isp_flow.fsm_stage_scheduled").id
                ):
                    return self.env.ref("fieldservice.mt_order_scheduled")
                if (
                    self.stage_id.id
                    == self.env.ref("fieldservice_isp_flow.fsm_stage_assigned").id
                ):
                    return self.env.ref("fieldservice.mt_order_assigned")
                if (
                    self.stage_id.id
                    == self.env.ref("fieldservice_isp_flow.fsm_stage_enroute").id
                ):
                    return self.env.ref("fieldservice.mt_order_enroute")
                if (
                    self.stage_id.id
                    == self.env.ref("fieldservice_isp_flow.fsm_stage_started").id
                ):
                    return self.env.ref("fieldservice.mt_order_started")
            except (ValueError, KeyError) as e:
                # External ID might not be available during certain operations
                # Fall back to parent implementation
                _logger.debug("External ID not available for stage tracking: %s", e)
                pass
        return super()._track_subtype(init_values)
