from geopy.geocoders import Nominatim

from odoo import _, models
from odoo.exceptions import ValidationError


class FsmOrder(models.Model):
    _inherit = "fsm.order"

    def save_location_from_browser(self, lat, lon):
        self.ensure_one()
        if self.location_id and not self.is_closed:
            geolocator = Nominatim(user_agent="myGeocoder")
            location = geolocator.reverse((lat, lon))
            if location:
                founeded_location = self.env["fsm.location"].search(
                    [("place", "=", location.raw.get("place_id"))], limit=1
                )
                if founeded_location:
                    self.write({"location_id": founeded_location.id})
                    return {"id": founeded_location.id, "name": founeded_location.name}

                new_location = self._create_new_location(location)
                self.write({"location_id": new_location.id})
                return {"id": new_location.id, "name": new_location.name}

    def _create_new_location(self, location):
        self.ensure_one()
        vals = self._get_location_values(location, self.location_id.name)
        partner_id = (
            self.env["res.partner"]
            .sudo()
            .create(
                {
                    "name": vals["name"],
                    "street": vals["street"],
                    "street2": vals["street2"],
                    "zip": vals["zip"],
                    "city": vals["city"],
                    "state_id": vals["state_id"],
                    "country_id": vals["country_id"],
                    "company_type": self.location_id.partner_id.company_type,
                }
            )
        )
        new_location = (
            self.env["fsm.location"]
            .sudo()
            .create(
                {
                    "name": vals["name"],
                    "partner_id": partner_id.id,
                    "owner_id": self.location_id.partner_id.id,
                }
            )
        )
        partner_id.write({"fsm_location": True})
        new_location.write(vals)
        new_location.geo_localize()
        return new_location

    def _get_location_values(self, location, name):
        address = location.raw.get("address", {})

        state_id = self.env["res.country.state"].search(
            [("name", "ilike", address.get("province", ""))], limit=1
        )

        country_id = self.env["res.country"].search(
            [("code", "ilike", address.get("country_code", ""))], limit=1
        )

        road = address.get("road", "")
        house_number = address.get("house_number", "")
        street = f"{road}, {house_number}".strip()

        city = address.get("town") or address.get("city") or ""
        street2 = address.get("village") or address.get("city_block") or ""
        postcode = address.get("postcode", "")
        if not road or not city or not postcode:
            raise ValidationError(
                _("Error: No address found in location data. Please try again.")
            )

        name_suffix = ", ".join(filter(None, [road, address.get("village")]))
        full_name = f"{name} ({name_suffix})" if name_suffix else name

        return {
            "name": full_name,
            "city": city,
            "state_id": state_id.id if state_id else False,
            "country_id": country_id.id if country_id else False,
            "zip": postcode,
            "street": street,
            "street2": street2,
            "place": location.raw.get("place_id"),
        }
