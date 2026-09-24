This module lets portal users see the field service equipments owned or
managed by their commercial partner (or equipments they follow) in the
"My Account" area of the portal.

It adds:

- an **Equipments** card on the portal home page with a record counter,
- a paginated list at `/my/equipments`,
- a detail page per equipment (product, location, owner, notes). Anonymous
  visitors can only open it through the link with the equipment's access
  token (`get_portal_url()`), which is the URL to use as a QR code target on
  physical equipment labels (see `fieldservice_equipment_portal_qrcode`).
