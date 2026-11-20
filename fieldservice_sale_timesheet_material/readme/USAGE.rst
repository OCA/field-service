#. Start from a confirmed **sale order** that generated a field service order
   (see *Field Service - Sale*), and make sure the order's **location** has an
   *Analytic Account* set (*Field Service - Analytic Accounting*).
#. On the field service order, record the time spent in the **Timesheets**
   tab, choosing a *Time Type* product for each line.
#. Record the materials consumed on site. These are the order's **done
   outgoing stock moves**, which *Field Service - Stock* only displays
   read-only — so a companion module is required to create them. Install
   **Field Service - Stock Request** (``fieldservice_stock_request``) and enter
   the products in the **Stock Requests** list of the order's *Inventory* tab,
   then process them through that module's flow until the moves reach the
   *Done* state. Materials delivered from the sale order appear here too. Only
   *Done* moves are billed.
#. Click **Add to Sale Order**. A line is added to the linked sale order for
   each *Time Type* product (with the total hours) and for each consumed
   product (with the net delivered quantity). The button is hidden when the
   order is not linked to a sale order.
#. Open the sale order with the **Sale Order** smart button and create the
   invoice as usual.

Clicking **Add to Sale Order** again only adds timesheets and materials that
have not been billed yet, so it is safe to use repeatedly as work progresses.

The **Service Order** report (*Print* menu on the field service order) is
extended with a **Time Spent** section listing each timesheet line with its
total, and a **Materials** section listing the *Done* stock moves per product
and direction (*Used* for outgoing moves, *Returned* for incoming ones), so the
printout shows both what was consumed on site and what came back.

Recommended product configuration:

The **service product on the original sale order** — the one that makes the
sale order generate the field service order — must have *Field Service
Tracking* set to *Per sale order* or *Per sale order line* (see *Field Service
- Sale*). That setting is what creates the field service order on sale
confirmation; without it there is no order to push the work back to.

The **time and material products** added by *Add to Sale Order*:

* *Time Type* products should be **services** measured in hours;
* the *Invoicing Policy* can be *Ordered quantities* or *Delivered
  quantities*: the delivered quantity of time lines is set from the recorded
  hours, while the delivered quantity of material lines comes from the field
  service order's own stock moves (which are linked to the created lines, so
  no extra delivery is generated);
* *Field Service Tracking* should be left at *Don't create FSM order*. The
  lines this module creates are already linked back to the originating field
  service order, so they never spawn further orders; but a *Per sale order
  line* setting would switch the line's delivered-quantity method to *Field
  Service* and override the quantity computed here.
