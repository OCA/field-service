# Copyright (C) 2019 Open Source Integrators
# Copyright (C) 2019 Serpent consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class FSMRouteDay(models.Model):
    _name = "fsm.route.day"
    _description = "Route Day"

    name = fields.Selection(
        selection=[
            ("Monday", _("Monday")),
            ("Tuesday", _("Tuesday")),
            ("Wednesday", _("Wednesday")),
            ("Thursday", _("Thursday")),
            ("Friday", _("Friday")),
            ("Saturday", _("Saturday")),
            ("Sunday", _("Sunday")),
        ],
    )

    def name_get(self):
        result = []
        for record in self:
            translated_value = dict(
                self._fields["name"]._description_selection(self.env)
            ).get(record.name, record.name)
            result.append((record.id, translated_value))
        return result
