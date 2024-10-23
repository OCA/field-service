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
        auto_join=True,
    )
    category_ids = fields.Many2many("fsm.category", string="Categories")
    calendar_id = fields.Many2one("resource.calendar", string="Working Schedule")
    mobile = fields.Char()
    territory_ids = fields.Many2many("res.territory", string="Territories")
    active = fields.Boolean(default=True)
    active_partner = fields.Boolean(
        related="partner_id.active", readonly=True, string="Partner is Active"
    )

    def toggle_active(self):
        for person in self:
            if not person.active and not person.partner_id.active:
                person.partner_id.toggle_active()
        return super().toggle_active()

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        res = super()._search(
            args=args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )
        # Check for args first having location_ids as default filter
        for arg in args:
            if isinstance(args, (list)):
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
                            "SELECT id "
                            "FROM fsm_location "
                            "WHERE complete_name like %s",
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
                    workers_ids = self.env.cr.fetchall()
                    if workers_ids:
                        preferred_workers_list = [worker[0] for worker in workers_ids]
                        return preferred_workers_list
        return res

    @api.model
    def create(self, vals):
        vals.update({"fsm_person": True})
        return super().create(vals)
