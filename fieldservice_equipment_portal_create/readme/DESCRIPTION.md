Let portal users register their own locations and equipments.

- `/my/locations/new`: register a location under the user's commercial
  partner (attached to its root FSM location when one exists).
- `/my/equipments/new`: register an equipment picking one of the partner's
  locations and a trackable, maintainable product. The **serial number is
  typed**, and the lot is found or created **under the selected product** —
  equipment, product and serial can never diverge.

Reads run as the portal user through ACLs and record rules scoped to the
commercial partner. Creations are server-controlled: whitelisted values with
ownership forced to the user's commercial partner (locations
delegation-inherit partners, which portal users cannot create) — direct RPC
creation stays blocked.
