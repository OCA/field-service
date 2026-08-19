# Copyright 2016 Cyril Gaudin (Camptocamp)
# Copyright 2015 Vauxoo
# Copyright 2009-2011  Akretion, Emmanuel Samyn, Benoît Guillot
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model
    def _get_default_instructions(self):
        """Get selected lines to add to exchange"""
        return self.env["return.instruction"].search(
            [("is_default", "=", True)], limit=1
        )

    warranty_duration = fields.Float(
        "Period",
        help="Warranty in month for this product/supplier relation. Only "
        "for company/supplier relation (purchase order) ; the  "
        "customer/company relation (sale order) always use the "
        "product main warranty field.",
    )
    warranty_return_partner = fields.Selection(
        [("company", "Company"), ("supplier", "Supplier"), ("other", "Other")],
        string="Return type",
        required=True,
        default="company",
        help="Who is in charge of the warranty return treatment toward the "
        "end customer. Company will use the current company "
        "delivery or default address and so on for supplier and "
        "brand manufacturer. Doesn't necessarily mean that the "
        "warranty to be applied is the one of the return partner "
        "(ie: can be returned to the company and be under the "
        "brand warranty).",
    )
    return_instructions = fields.Many2one(
        "return.instruction",
        "Instructions",
        default=lambda self: self._get_default_instructions(),
        help="Instructions for product return.",
    )
    active_supplier = fields.Boolean(
        help="Is this supplier still active, only for information."
    )
    warranty_return_address = fields.Many2one(
        "res.partner",
        compute="_compute_warranty_return_address",
        string="Return address",
        help="Where the goods should be returned  "
        "(computed field based on other infos.)",
    )
    warranty_return_other_address = fields.Many2one(
        "res.partner",
        string="Return other address",
        help="Where the customer has to send back the product(s) "
        "if warranty return is set to 'other'.",
    )

    @api.depends("warranty_return_partner")
    def _compute_warranty_return_address(self):
        """Method to return the partner delivery address or if none, the
        default address
        """
        for record in self:
            return_partner = record.warranty_return_partner
            partner_id = record.company_id.partner_id.id
            if return_partner and return_partner == "supplier":
                partner_id = record.partner_id.id
            elif (
                return_partner
                and return_partner == "company"
                and record.company_id.crm_return_address_id
            ):
                partner_id = record.company_id.crm_return_address_id.id
            elif (
                return_partner
                and return_partner == "other"
                and record.warranty_return_other_address
            ):
                partner_id = record.warranty_return_other_address.id
            record.warranty_return_address = partner_id
