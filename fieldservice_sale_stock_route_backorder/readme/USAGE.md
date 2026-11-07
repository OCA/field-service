To use this module, you need to:

**For this module to work as intended, you need to enable the Auto
Validate FSM Pickings setting in Field Service \> Configuration \>
Settings.**

1.  Navigate to Sales \> Orders.
2.  Create a new sales order.
3.  Add a product that generates an FSM order (Field Service Tracking
    set to "Create one FSM order per sale order" on the product form).
    If you want this product to generate a backorder sale whenever it is
    not fully delivered, ensure the field **Create Backorder Sale
    Order** is checked on the product form
4.  Set the Customer and FSM Location.
5.  Make sure the FSM Location has a route set and this route has a
    person assigned and route days set.
6.  In the sale order, navigate to the 'Other Info' tab and set the
    'Delivery Date' and 'Delivery End Date' fields. You can also leave
    them empty to have the system automatically assign the next
    available route day.
7.  Confirm the sale order.
8.  Enter the FSM order. A new 'Adjust Delivery' button is available in
    the header.
9.  Click the 'Adjust Delivery' button to open the wizard. Set the
    quantity to deliver for each product and, if necessary, add new
    products to the delivery. Proceed to confirm the wizard.
10. The system will attempt to **reserve newly available stock** before
    delivery for storable products. It will allow **delivering more than
    the initial demand** if additional unreserved stock is available. It
    will prevent delivery of quantities exceeding the **total available
    stock** (reserved + free stock in the warehouse). For consumable
    products, the system will always allow over-delivery.
11. Once confirmed, the system will validate the picking and create a
    backorder for any remaining quantities. This backorder will be
    scheduled for the next available route day based on the FSM
    location's route configuration and both the FSM order and sale order
    schedule will be updated.
12. When all quantities have been delivered, the FSM order will be
    marked as completed automatically.
