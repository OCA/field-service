from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    visit_crm_team_id = fields.Many2one(
        "crm.team",
        string="Visit CRM Team",
        check_company=True,
        help="CRM team assigned to site-survey requests.",
    )
    visit_sale_order_template_id = fields.Many2one(
        "sale.order.template",
        string="Visit Booking Template",
        check_company=True,
        help="Quotation template used when a customer books a site visit.",
    )
    requests_sale_order_template_id = fields.Many2one(
        "sale.order.template",
        string="Maintenance Request Template",
        check_company=True,
        help="Quotation template used when a customer submits a maintenance request.",
    )
    visit_confirmation_policy = fields.Selection(
        [
            ("phone", "Phone Verification"),
            ("payment", "Online Payment"),
        ],
        string="Visit Confirmation Policy",
        required=True,
        default="phone",
        help=(
            "Phone Verification keeps the selected appointment reserved on a draft "
            "quotation until staff call the customer and confirm it. Online Payment "
            "confirms the quotation only after full online payment."
        ),
    )
    installation_release_policy = fields.Selection(
        [
            ("approval", "Approval"),
            ("payment", "Online Payment"),
        ],
        string="Installation Release Policy",
        required=True,
        default="payment",
        help=(
            "Approval lets the customer schedule installation after the quotation is "
            "confirmed. Online Payment releases scheduling only after full payment."
        ),
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    visit_crm_team_id = fields.Many2one(
        related="company_id.visit_crm_team_id",
        readonly=False,
        store=False,
    )
    visit_sale_order_template_id = fields.Many2one(
        related="company_id.visit_sale_order_template_id",
        readonly=False,
        store=False,
    )
    requests_sale_order_template_id = fields.Many2one(
        related="company_id.requests_sale_order_template_id",
        readonly=False,
        store=False,
    )
    visit_confirmation_policy = fields.Selection(
        related="company_id.visit_confirmation_policy",
        readonly=False,
        store=False,
    )
    installation_release_policy = fields.Selection(
        related="company_id.installation_release_policy",
        readonly=False,
        store=False,
    )
