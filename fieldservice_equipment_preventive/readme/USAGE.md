1. *Field Service > Configuration > Orders > Preventive Visit Types*: review
   the visit types (preventive maintenance, calibration and certification are
   provided).
2. On each equipment, tab *Preventive Visits*: list the visit types it needs,
   with their interval in months, the last visit date and optionally the
   template of the work to perform.
3. Create a recurring order for the location, tick *Preventive Visit* and
   optionally restrict it to some visit types. The *Equipments* smart button
   shows what the plan covers, and a banner warns about equipments whose visit
   has no template.

Each generated order lists the visits due on or before the date of the
following visit of the plan (or its own date, when no visit follows within a
year), most overdue first. Dates are compared as calendar dates in the time
zone of the user; when a visit is already listed in an earlier open order, it
is considered done on that date. Lines left pending when an order is completed
are carried over to the top of the next open order of the plan.
