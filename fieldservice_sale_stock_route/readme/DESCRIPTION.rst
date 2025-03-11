This module integrates the `fieldservice_sale_stock` and `fieldservice_route` modules, enabling automatic generation of FSM order day routes from sales orders.

Requirements for Confirming a Sales Order
-----------------------------------------
If a sales order contains a product that generates an FSM order, the following conditions must be met before confirmation:

- An FSM location must be set.
- The FSM location must have an assigned route.
- The FSM route must have a designated FSM person.
- The FSM route must have assigned working days.

Automatic Scheduling of FSM Orders
----------------------------------
- If the `commitment_date` and `commitment_date_end` fields **are not set** on the sale order upon confirmation, they will be automatically assigned to the next available route day based on the FSM location’s schedule.
- If these fields **are set**, the FSM order will be scheduled accordingly, with validation ensuring that the `commitment_date` falls on a valid route day. This validation can be overridden by enabling the **"Force Schedule"** option on the FSM route to allow scheduling on any day.

This module also introduces a **"Postpone Delivery"** button in the FSM order form view, allowing users to reschedule the order to the next available route day based on the FSM location’s schedule.
