# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _name = "fsm.person"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread.blacklist", "fsm.model.mixin"]
    _description = "Field Service Worker"
    _stage_type = "worker"

    partner_id = fields.Many2one(
        "res.partner",
        string="Related Partner",
        required=True,
        ondelete="restrict",
        delegate=True,
    )
    category_ids = fields.Many2many("fsm.category", string="Categories")
    calendar_id = fields.Many2one("resource.calendar", string="Working Schedule")
    mobile = fields.Char()
    territory_ids = fields.Many2many("res.territory", string="Territories")
    active = fields.Boolean(default=True)
    active_partner = fields.Boolean(
        related="partner_id.active", readonly=True, string="Partner is Active"
    )

    def action_unarchive(self):
        for person in self:
            if not person.partner_id.active:
                person.partner_id.action_unarchive()
        return super().action_unarchive()

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        *,
        active_test=True,
        bypass_access=False,
    ):
        res = super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            active_test=active_test,
            bypass_access=bypass_access,
        )
        # Check for args first having location_ids as default filter
        for arg in args:
            if isinstance(args, list) and arg[0] == "location_ids":
                # If given int search ID, else search name
                if isinstance(arg[2], int):
                    self.env.cr.execute(
                        "SELECT person_id "
                        "FROM fsm_location_person "
                        "WHERE location_id=%s",
                        (arg[2],),
                    )
                else:
                    arg_2 = "%" + arg[2] + "%"
                    self.env.cr.execute(
                        "SELECT id FROM fsm_location WHERE complete_name like %s",
                        (arg_2,),
                    )
                    location_ids = self.env.cr.fetchall()
                    if location_ids:
                        location_ids = [location[0] for location in location_ids]
                        self.env.cr.execute(
                            "SELECT DISTINCT person_id "
                            "FROM fsm_location_person "
                            "WHERE location_id in %s",
                            [tuple(location_ids)],
                        )
                workers_ids = [row[0] for row in self.env.cr.fetchall()]
                return self.browse(workers_ids)._as_query()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update({"fsm_person": True})
        return super().create(vals_list)
