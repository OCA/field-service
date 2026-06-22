from odoo import models


class FsmLocation(models.Model):
    _inherit = "fsm.location"

    def write(self, vals):
        # Overrride to propagate address changes to linked partner
        # particularly for zip code changes
        # If not, this will end up with inconsistent data between
        # fsm.location and res.partner and then it will
        # throw errors when trying to use the zip_id
        for record in self:
            partner = record.partner_id
            if not partner:
                continue

            vals = vals.copy()

            zip_id = vals.get("zip_id") or (record.zip_id.id or False)
            zip_rec = self.env["res.city.zip"].browse(zip_id) if zip_id else False
            new_zip = vals.get("zip", record.zip)

            if zip_rec and zip_rec.exists() and zip_rec.name != new_zip:
                vals["zip_id"] = False
                if partner.zip_id:
                    partner.zip_id = False

            partner_updates = {
                key: vals[key]
                for key in [
                    "zip",
                    "city",
                    "state_id",
                    "country_id",
                    "street",
                    "street2",
                ]
                if key in vals
                and vals[key]
                != (
                    getattr(partner, key).id
                    if key.endswith("_id")
                    else getattr(partner, key)
                )
            }

            if partner_updates:
                partner.write(partner_updates)

        return super().write(vals)
