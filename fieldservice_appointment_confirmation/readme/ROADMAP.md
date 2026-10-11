* Worker availability relies on the worker `resource.calendar` (with a company
  fallback). Workers without any working schedule will not expose slots.
* Appointments are shown in the Field Service calendar only; they are not
  pushed to the general Odoo calendar (`calendar.event` / Meetings).
