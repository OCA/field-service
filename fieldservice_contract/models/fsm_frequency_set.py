from odoo import models, api


class FSMFrequencySet(models.Model):
    _inherit = "fsm.frequency.set"

    def _get_theoretical_order_count_by_period(self,period_first_date,period_last_date):
        self.ensure_one()
        if not period_first_date or not period_last_date:
            return False
        rrules = self._get_rruleset(
            dtstart=period_first_date, until=period_last_date
        )
        return len([date for date in rrules])
