On a service order, tab *Equipments*, section *Checklist*: add one line per
equipment to check and mark each line with the *Done*, *Not Found* or *Back to
Pending* buttons while on site. The state is only changed by these buttons, so
that *Done* always records its date. The number of pending lines is shown above
the checklist.

The checklist is the source of truth for the *Equipments* it lists: an
equipment is added to the order with its first line, follows the line when its
equipment is changed, and is removed with its last line. Equipments added
directly to the order are not turned into checklist lines and are never removed
by the checklist.

Checklist lines follow the company of their order, and only equipments of that
company can be selected.
