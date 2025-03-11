To use this module, you need to:

1. Navigate to Sales > Orders.
2. Create a new sales order.
3. Add a product that generates an FSM order (Field Service Tracking set to "Create one FSM order per sale order" on the product form).
4. Set the Customer and FSM Location.
5. Make sure the FSM Location has a route set and this route has a person assigned and route days set.
6. In the sale order, navigate to the 'Other Info' tab and set the 'Delivery Date' and 'Delivery End Date' fields. You can also leave them empty to have the system automatically assign the next available route day.
7. Confirm the sale order.
8. If the 'Delivery Date' and 'Delivery End Date' fields were empty, the system will automatically assign the next available route day based on the FSM location's schedule. If they were set, the FSM order will be scheduled accordingly. In case the 'Delivery Date' falls on a day that is not part of the route, the system will show an error message.

If you navigate to the FSM order, you will see that the Schedule Details are based on the 'Delivery Date' and 'Delivery End Date' fields from the sale order. 

Additionally, you will find a 'Postpone Delivery' button in the FSM order form view, allowing you to reschedule the order to the next available route day based on the FSM location's schedule. You can also manually reschedule the order by changing the 'Delivery Date' and 'Delivery End Date' fields in the sale order.
