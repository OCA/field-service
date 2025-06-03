1. **Configure Field Service Products:**
- Navigate to the `Field Service` module.
- Under `Master Data` > `Products`, create or edit a product.
- In the `Sales` tab, enable the **Create one FSM order per sale order** option.
- Save the product.

2. **Configure Portal User:**
- Navigate to the `Contacts` module.
- Create or edit a contact.
- In the `Action` tab, execute the **Convert to FSM Record** option, select the `Location` record type.
- Grant portal access to this contact.
- Save the contact.

3. **Configure FSM Location**
- Navigate to the `Field Service` module.
- Under `Master Data` > `Locations`, edit the created location.
- Assign a route to the location. Ensure the route has a person assigned to it and days of the week are specified. Adjust the route's maximum capacity as desired.
- Save the location.

4. **Configure FSM Delivery Time Ranges**
- Navigate to the `Field Service` module.
- Under `Configuration` > `Availability` > `Delivery Time Ranges`, create delivery time ranges.
- When the `Route` field is specified, the delivery time range is used on the related route only. When the `Route` field is empty, the delivery time range is used on all routes.
- Save the delivery time ranges.
- You can also set a default delivery time range in the `Field Service` module under `Configuration` > `Settings` > `Website Sales` > `Auto-assign Default Delivery Time Range`. This will be used when a delivery date is selected during the checkout process, but no specific delivery time range is selected.

5. **Configure Maximum Allowed Time for Order Placement**
- Navigate to the `Field Service` module.
- Under `Configuration` > `Settings` > `Website Sales`, configure the maximum allowed time for order placement.
- This setting determines the maximum number of days in advance that a customer can place an order.
- Save the settings.

6. **Create a Sale Order from the E-Commerce:**
- Log in to the e-commerce portal using the portal user created earlier.
- Navigate to the shop and select a field service product.
- Add the product to the cart and proceed to checkout.
- At the `Confirm Order` step, select the preferred delivery date and time range. If no route is assigned to the selected delivery address, the checkout process can't be completed.
- Complete the checkout process. To confirm the sale order, if specified in the configuration, the signature and payment must be completed.

7. **Validate the process:**
- Navigate to the `Sales` module.
- Under `Orders`, you will see the new sale order created and confirmed.
- This sale order will be linked to a stock picking and an FSM order, where both will have the same delivery start and end dates based on the customer's selection in the e-commerce platform.
- The FSM order will be assigned to the appropriate day route, based on the delivery date selected by the customer.

This process can also be completed manually. When creating a sale order, navigate to the `Other Info` tab and select the prefered **Delivery Date and Delivery End Date** fields to define the delivery window. The sale order cannot be confirmed unless the selected Delivery Date falls on an available day route.

Specific days can be blocked for delivery during the checkout process by creating `fsm_blackout_day` records. The `fsm_blackout_day` records can be created under `Field Service` > `Configuration` > `Availabiliy` > `Blackout Days`.
