This module lets you send materials out to a Field Service location and
receive materials back from it directly from the Field Service Order, using
standard stock transfers (pickings).

On the Field Service Order you can:

* list the outgoing and the incoming products;
* choose the operation type (``stock.picking.type``) used for the outgoing
  and for the incoming transfer;
* create the outgoing and/or incoming transfer in a single click; a transfer
  is only created when there are products that are not part of a transfer yet.

The outgoing and incoming operation types can be pre-set on the Field Service
Order Template. When a template is selected on an order, its operation types
are applied and take precedence over the warehouse defaults.

The created transfers are left in draft and are processed by the user through
the standard transfer flow (mark as todo, check availability, validate).

Outgoing and incoming transfers are reachable from the Field Service Order
through the *Deliveries* and *Returns* smart buttons provided by
``fieldservice_stock``.
