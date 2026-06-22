# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class FSMActivity(models.Model):
    _name = "fsm.activity"
    _description = "Field Service Activity"

    name = fields.Char(required=True)
    required = fields.Boolean()
    sequence = fields.Integer()
    completed = fields.Boolean()
    completed_on = fields.Datetime(readonly=True)
    completed_by = fields.Many2one("res.users", readonly=True)
    ref = fields.Char("Reference")
    fsm_order_id = fields.Many2one("fsm.order", "FSM Order")
    fsm_template_id = fields.Many2one("fsm.template", "FSM Template")
    state = fields.Selection(
        [("todo", "To Do"), ("done", "Completed"), ("cancel", "Cancelled")],
        readonly=True,
        default="todo",
    )

    @property
    def _protected_fields(self) -> tuple[str]:
        """Fields that should not be modified on a "done" activity"""
        return ("name", "required", "ref")

    def write(self, vals):
        if any(fname in vals for fname in self._protected_fields) and any(
            rec.state != "todo" for rec in self.with_context(prefetch_fields=False)
        ):
            fnames = list(set(self._protected_fields) & set(vals.keys()))
            field_strings = [
                self._fields[fname]._description_string(self.env) for fname in fnames
            ]
            state_string = dict(
                self._fields["state"]._description_selection(self.env)
            ).get(self.state)
            raise ValidationError(
                _(
                    "It is forbidden to modify the following fields in a %(state)r "
                    "Activity:\n%(fields)s",
                    state=state_string,
                    fields="\n".join(field_strings),
                )
            )
        return super().write(vals)

    def action_done(self):
        self.write(
            {
                "completed": True,
                "completed_on": fields.Datetime.now(),
                "completed_by": self.env.user.id,
                "state": "done",
            }
        )

    def action_cancel(self):
        self.state = "cancel"
