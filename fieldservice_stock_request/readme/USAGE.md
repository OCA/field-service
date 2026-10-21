To request stock from a field service order:

- Create a field service order and set its location. The warehouse of
  the order is the one the stock is requested from.
- In the Inventory tab, add a line per product with its quantity, the
  expected date and the direction: *Outbound* to bring the products to
  the service location, *Inbound* to return them to the warehouse.
- The first line creates a stock request order linked to the field
  service order. The next lines with the same warehouse and direction
  are added to that stock request order while it is in draft.
- Click *Submit* to submit the stock requests for approval. *Cancel*
  and *Set to Draft* cancel them or bring them back to draft. The
  request state of the field service order follows them.
- Once a stock request is confirmed, its transfers are created in the
  Inventory app. Validating them updates the quantities done on the
  lines of the field service order.
