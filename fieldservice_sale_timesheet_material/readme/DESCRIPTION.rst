This module lets you invoice the **time** spent and the **materials** consumed
on a field service order by adding them as lines to the order's sale order,
which can then be invoiced through the standard sales flow.

It applies to field service orders that were **generated from a sale order**
(see *Field Service - Sale*): the recorded work is pushed back to that same
sale order. It builds on ``fsm.order``:

* timesheets are the ``account.analytic.line`` records linked to the order
  (from *Field Service - Analytic Accounting*), grouped by their *Time Type*
  product;
* materials are the consumed stock moves of the order (from
  *Field Service - Stock*), grouped by product. ``fieldservice_stock`` only
  displays these moves read-only, so creating them requires a companion module
  such as **Field Service - Stock Request** (``fieldservice_stock_request``),
  or deliveries coming from the sale order.

A single **Add to Sale Order** button on the field service order pushes both
timesheets and materials onto the linked sale order. The button is only shown
when the order is linked to a sale order; it never creates one. The operation
is idempotent: only work that has not yet been billed is added.
