# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class Agreement(models.Model):
    _name = "agreement"
    _description = "Agreement"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _code_uniq = models.Constraint(
        "unique(code, commercial_partner_id, company_id)",
        "This agreement code already exists for this commercial entity!",
    )

    code = fields.Char(required=True, tracking=True)
    name = fields.Char(required=True, tracking=True, translate=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        ondelete="restrict",
        tracking=True,
    )
    commercial_partner_id = fields.Many2one(
        "res.partner",
        string="Commercial Entity",
        compute="_compute_commercial_partner_id",
        tracking=True,
        precompute=True,
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    is_template = fields.Boolean(
        string="Is a Template?",
        copy=False,
        help="Set if the agreement is a template. "
        "Template agreements don't require a partner.",
    )
    agreement_type_id = fields.Many2one(
        "agreement.type",
        string="Agreement Type",
        help="Select the type of agreement",
    )
    domain = fields.Selection(
        selection="_domain_selection",
        compute="_compute_domain",
        tracking=True,
        store=True,
        readonly=False,
    )
    active = fields.Boolean(default=True)
    signature_date = fields.Date(tracking=True)
    start_date = fields.Date(tracking=True, help="When the agreement starts.")
    end_date = fields.Date(tracking=True, help="When the agreement ends.")

    @api.model
    def _domain_selection(self):
        return [
            ("sale", self.env._("Sale")),
            ("purchase", self.env._("Purchase")),
        ]

    @api.depends("partner_id")
    def _compute_commercial_partner_id(self):
        for rec in self:
            rec.commercial_partner_id = rec.partner_id.commercial_partner_id

    @api.depends("agreement_type_id")
    def _compute_domain(self):
        for rec in self:
            if rec.agreement_type_id and rec.agreement_type_id.domain:
                rec.domain = rec.agreement_type_id.domain
            else:
                rec.domain = "sale"

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}"

    def copy(self, default=None):
        """Always assign a value for code because is required"""
        default = dict(default or {})
        if default.get("code", False):
            return super().copy(default)
        default.setdefault("code", self.env._("%(code)s (copy)", code=self.code))
        return super().copy(default)
