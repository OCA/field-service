This module lets you invoice the **time** spent and the **materials**
consumed on a field service order by adding them as lines to the order's
sale order, which can then be invoiced through the standard sales flow.

It applies to field service orders that were **generated from a sale
order** (see *Field Service - Sale*): the recorded work is pushed back
to that same sale order. It builds on `fsm.order`:

- timesheets are the `account.analytic.line` records linked to the order,
  grouped by their *Time Type* product. They are recorded in the
  **Timesheets** tab of *Field Service - Timesheet*, which this module
  shows on every order, not only on orders with a project;
- materials are the consumed stock moves of the order (from *Field
  Service - Stock*), grouped by product. `fieldservice_stock` only
  displays these moves read-only, so creating them requires a companion
  module such as **Field Service - Stock Request**
  (`fieldservice_stock_request`). Deliveries that are already linked to
  a sale order line are left on it.

A single **Add to Sale Order** button on the field service order pushes
both timesheets and materials onto the linked sale order. The button is
only shown when the order is linked to a sale order; it never creates
one. The operation is idempotent: only work that has not yet been billed
is added.
