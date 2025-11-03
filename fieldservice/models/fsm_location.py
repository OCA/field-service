# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.api import Self


class FSMLocation(models.Model):
    _name = "fsm.location"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin", "fsm.model.mixin"]
    _description = "Field Service Location"
    _parent_name = "parent_id"
    _parent_store = True
    _stage_type = "location"
    _rec_names_search = ["complete_name"]

    direction = fields.Char()
    partner_id = fields.Many2one(
        "res.partner",
        string="Related Partner",
        required=True,
        ondelete="restrict",
        delegate=True,
        auto_join=True,
    )
    owner_id = fields.Many2one(
        "res.partner",
        string="Related Owner",
        required=True,
        ondelete="restrict",
        auto_join=True,
    )
    contact_id = fields.Many2one(
        "res.partner",
        string="Primary Contact",
        domain="[('is_company', '=', False)," " ('fsm_location', '=', False)]",
        index=True,
    )
    description = fields.Char()
    territory_id = fields.Many2one("res.territory", string="Territory")
    branch_id = fields.Many2one("res.branch", string="Branch")
    district_id = fields.Many2one("res.district", string="District")
    region_id = fields.Many2one("res.region", string="Region")
    territory_manager_id = fields.Many2one(
        string="Primary Assignment", related="territory_id.person_id"
    )
    district_manager_id = fields.Many2one(
        string="District Manager", related="district_id.partner_id"
    )
    region_manager_id = fields.Many2one(
        string="Region Manager", related="region_id.partner_id"
    )
    branch_manager_id = fields.Many2one(
        string="Branch Manager", related="branch_id.partner_id"
    )

    calendar_id = fields.Many2one("resource.calendar", string="Office Hours")
    parent_id = fields.Many2one("fsm.location", string="Parent", index=True)
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        string="Children Locations",
        comodel_name="fsm.location",
        inverse_name="parent_id",
        readonly=True,
    )
    notes = fields.Text(string="Location Notes")
    person_ids = fields.One2many("fsm.location.person", "location_id", string="Workers")
    contact_count = fields.Integer(
        string="Contacts Count", compute="_compute_contact_count"
    )
    equipment_count = fields.Integer(
        string="Equipment", compute="_compute_equipment_count"
    )
    sublocation_count = fields.Integer(
        string="Sub Locations", compute="_compute_sublocation_count"
    )
    complete_name = fields.Char(
        compute="_compute_complete_name",
        recursive=True,
        store=True,
    )
    complete_direction = fields.Char(
        compute="_compute_complete_direction",
        store=True,
        recursive=True,
    )

    # This field is added for backward compatibility. But it's deprecated.
    # Use `parent_id` instead.
    # TODO: Remove this field in the 19.0 migration.
    fsm_parent_id = fields.Many2one(string="Deprecated Parent", related="parent_id")

    @api.model_create_multi
    def create(self, vals):
        res = super().create(vals)
        res.write({"fsm_location": True})
        return res

    @api.depends("partner_id.name", "parent_id.complete_name", "ref")
    def _compute_complete_name(self):
        for loc in self:
            name = loc.partner_id.name
            if loc.ref:
                name = f"[{loc.ref}] {name}"
            if loc.parent_id:
                name = f"{loc.parent_id.complete_name} / {name}"
            loc.complete_name = name

    @api.depends("direction", "parent_id.complete_direction")
    def _compute_complete_direction(self):
        for rec in self:
            parent_direction = rec.parent_id.complete_direction
            complete_direction = (parent_direction or "") + (rec.direction or "")
            rec.complete_direction = complete_direction or False

    @api.onchange("parent_id")
    def _onchange_parent_id(self):
        self.owner_id = self.parent_id.owner_id
        self.contact_id = self.parent_id.contact_id
        self.direction = self.parent_id.direction
        self.street = self.parent_id.street
        self.street2 = self.parent_id.street2
        self.city = self.parent_id.city
        self.zip = self.parent_id.zip
        self.state_id = self.parent_id.state_id
        self.country_id = self.parent_id.country_id
        self.tz = self.parent_id.tz
        self.territory_id = self.parent_id.territory_id

    @api.onchange("territory_id")
    def _onchange_territory_id(self):
        self.territory_manager_id = self.territory_id.person_id or False
        self.branch_id = self.territory_id.branch_id or False
        if self.env.company.auto_populate_persons_on_location:
            person_vals_list = []
            for person in self.territory_id.person_ids:
                person_vals_list.append(
                    (0, 0, {"person_id": person.id, "sequence": 10})
                )
            self.person_ids = self.territory_id and person_vals_list or False

    @api.onchange("branch_id")
    def _onchange_branch_id(self):
        self.branch_manager_id = self.territory_id.branch_id.partner_id or False
        self.district_id = self.branch_id.district_id or False

    @api.onchange("district_id")
    def _onchange_district_id(self):
        self.district_manager_id = self.branch_id.district_id.partner_id or False
        self.region_id = self.district_id.region_id or False

    @api.onchange("region_id")
    def _onchange_region_id(self):
        self.region_manager_id = self.region_id.partner_id or False

    def action_view_contacts(self):
        """
        This function returns an action that display existing contacts
        of given fsm location id and its child locations. It can
        either be a in a list or in a form view, if there is only one
        contact to show.
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "contacts.action_contacts"
        )
        action["context"] = dict(self.env.context, default_service_location_id=self.id)
        domain = [("service_location_id", "child_of", self.ids)]
        contacts = self.env["res.partner"].search(domain)
        if len(contacts) == 1:
            action["views"] = [(None, "form")]
            action["res_id"] = contacts.id
        else:
            action["domain"] = domain
        return action

    def _compute_contact_count(self):
        if not self.ids:  # pragma: no cover
            self.contact_count = 0
            return
        count_by_location = dict[Self, int](
            self.env["res.partner"]._read_group(
                domain=[("service_location_id", "child_of", self.ids)],
                groupby=["service_location_id"],
                aggregates=["__count"],
            )
        )
        for loc in self:
            loc.contact_count = sum(
                contact_count
                for location, contact_count in count_by_location.items()
                if location.parent_path.startswith(loc.parent_path)
            )

    def action_view_equipment(self):
        """
        This function returns an action that display existing
        equipment of given fsm location id. It can either be a in
        a list or in a form view, if there is only one equipment to show.
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice.action_fsm_equipment"
        )
        domain = [("location_id", "child_of", self.ids)]
        equipment = self.env["fsm.equipment"].search(domain)
        if len(equipment) == 1:
            action["views"] = [(None, "form")]
            action["res_id"] = equipment.id
        else:
            action["domain"] = domain
        return action

    def _compute_sublocation_count(self):
        if not self.ids:  # pragma: no cover
            self.sublocation_count = 0
            return
        count_by_location = dict[Self, int](
            self.env["fsm.location"]._read_group(
                domain=[
                    ("parent_id", "child_of", self.ids),
                    ("parent_id", "!=", False),
                ],
                groupby=["parent_id"],
                aggregates=["__count"],
            )
        )
        for loc in self:
            loc.sublocation_count = sum(
                child_count
                for location, child_count in count_by_location.items()
                if location.parent_path.startswith(loc.parent_path)
            )

    def action_view_sublocation(self):
        """
        This function returns an action that display existing
        sub-locations of a given fsm location id. It can either be a in
        a list or in a form view, if there is only one sub-location to show.
        """
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice.action_fsm_location"
        )
        domain = [("parent_id", "child_of", self.ids), ("id", "not in", self.ids)]
        sublocations = self.env["fsm.location"].search(domain)
        if len(sublocations) == 1:
            action["views"] = [(None, "form")]
            action["res_id"] = sublocations.id
        else:
            action["domain"] = domain
        return action

    def geo_localize(self):
        return self.partner_id.geo_localize()

    def _compute_equipment_count(self):
        if not self.ids:  # pragma: no cover
            self.equipment_count = 0
            return
        count_by_location = dict[Self, int](
            self.env["fsm.equipment"]._read_group(
                domain=[("location_id", "child_of", self.ids)],
                groupby=["location_id"],
                aggregates=["__count"],
            )
        )
        for loc in self:
            loc.equipment_count = sum(
                equipment_count
                for location, equipment_count in count_by_location.items()
                if location.parent_path.startswith(loc.parent_path)
            )

    @api.onchange("country_id")
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange("state_id")
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id


class FSMPerson(models.Model):
    _inherit = "fsm.person"

    location_ids = fields.One2many(
        "fsm.location.person", "person_id", string="Linked Locations"
    )
