# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import Domain


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
        bypass_search_access=True,
    )
    state_id = fields.Many2one(
        related="partner_id.state_id",
        store=True,
        inherited=True,
        readonly=False,
        domain="[('country_id', '=?', country_id)]",
    )
    category_ids = fields.Many2many("fsm.category", string="Categories")
    calendar_id = fields.Many2one("resource.calendar", string="Working Schedule")
    mobile = fields.Char()
    territory_ids = fields.Many2many("res.territory", string="Territories")
    active = fields.Boolean(default=True)
    active_partner = fields.Boolean(
        related="partner_id.active", readonly=True, string="Partner is Active"
    )
    team_id = fields.Many2one("fsm.team", string="Team")

    def action_unarchive(self):
        self.with_context(active_test=False).partner_id.action_unarchive()
        return super().action_unarchive()

    @api.model
    def _search(
        self,
        domain,
        offset=0,
        limit=None,
        order=None,
        *,
        active_test: bool = True,
        bypass_access: bool = False,
    ):
        res = super()._search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
        )
        # Check for args first having location_ids as default filter
        for arg in domain:
            if isinstance(domain, (list, Domain)):
                if arg[0] == "location_ids":
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
                    workers_ids = set()
                    for id_ in self.env.cr.fetchall():
                        workers_ids.add(id_[0])
                    return self.browse(workers_ids)._as_query()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.update({"fsm_person": True})
        return super().create(vals_list)
