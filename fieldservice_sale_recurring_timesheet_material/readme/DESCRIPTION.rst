This module is a bridge between *Field Service - Sales - Recurring*
(``fieldservice_sale_recurring``) and *Field Service - Sale Timesheet &
Material* (``fieldservice_sale_timesheet_material``). It is installed
automatically when both are.

A recurring order sold on a sale order generates its field service orders from
its frequency rules. Those orders are linked to the **sale order line** that
sold the recurring order, and not to a sale order of their own, so the **Add to
Sale Order** button was hidden on them and the time and materials they recorded
could not be billed.

With this module:

* the button is shown on those orders as well, and adds their timesheets and
  consumed materials to the sale order that sold the recurring order;
* the recurring order gets its own **Add to Sale Order** button, which does the
  same for all its orders in one go;
* the invoice lines generated from those sale order lines are linked to the
  field service order whose work they bill, so the order shows its invoices
  and the invoice shows its orders, as for any other field service order.
