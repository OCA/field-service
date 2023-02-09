# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _
from odoo.exceptions import ValidationError


def validate_stage_fields(records):
    for rec in records:
        stage = rec.stage_id
        field_ids = stage.validate_field_ids
        field_names = [x.name for x in field_ids]
        values = rec.read(field_names)

        for field in field_ids:
            if not values[0][field.name]:
                raise ValidationError(
                    _(
                        'Cannot move to stage "%s" '
                        'until the "%s" field is set.'
                        % (stage.name, field.field_description)
                    )
                )
