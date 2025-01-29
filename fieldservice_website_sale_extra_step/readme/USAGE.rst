1. **Enable e-commerce's extra step**
- Navigate to Website > Go To Website > Cart Icon > Customize > Enable 'Extra Step Option'.

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
- Under `Master Data` > `Delivery Time Ranges`, create delivery time ranges.
- When the `Route` field is specified, the delivery time range is used on the related route only. When the `Route` field is empty, the delivery time range is used on all routes.
- Save the delivery time ranges.

5. **Configure Field Service Products:**
- Navigate to the `Field Service` module.
- Under `Master Data` > `Products`, create or edit a product.
- In the `Sales` tab, enable the **Create one FSM order per sale order** option.
- Save the product.

6. **Create a Sale Order from the E-Commerce:**
- Log in to the e-commerce portal using the portal user created earlier.
- Navigate to the shop and select a field service product.
- Add the product to the cart and proceed to checkout.
- At the `Extra Info` step, add the information.
- Complete the checkout process. To confirm the sale order, if specified in the configuration, the signature and payment must be completed.

7. **Validate the process:**
- Navigate to the `Sales` module.
- Under `Orders`, you will see the new sale order created and confirmed.
- This sale order will be linked to an FSM order, which will contain the extra step information from the sale order.
