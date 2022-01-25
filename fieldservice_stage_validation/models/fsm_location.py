# Copyright (C) 2020 Brian McMaster <brian@mcmpest.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class FSMLocation(models.Model):
    _inherit = 'fsm.location'

    @api.constrains('stage_id')
    def _validate_stage_fields(self):
        for rec in self:
            stage = rec.stage_id
            field_names = [x.name for x in stage.validate_field_ids]

            for name in field_names:
                if not rec[name]:
                    raise ValidationError(_('Cannot move to stage "%s" '
                                            'until the "%s" field is set.'
                                            % (stage.name, name)))
