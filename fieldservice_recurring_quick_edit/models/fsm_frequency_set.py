# Copyright (C) 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.rrule import rruleset

from odoo import fields, models


class FSMFrequencySet(models.Model):
    _inherit = 'fsm.frequency.set'

