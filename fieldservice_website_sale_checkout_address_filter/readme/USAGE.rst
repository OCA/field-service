1. Create a contact. Fill in the address and email fields.
2. Create a child contact of the previous one of type 'Delivery Address' or 'Other Address'. Fill in the name, address, and email fields.
3. Grant portal access to the parent contact.
4. Convert both contacts to FSM location records. Make sure both these locations have a route assigned and that the route has the following fields filled in:

   - Name
   - Person
   - Days
   - Maximum (set to a value greater than 0)

5. Optionally, navigate to Website > Configuration > Settings and enable the "Filter Shipping for Child Contacts" and "Disable Express Checkout" options.
6. Log in to the website as the parent contact, add an item to the cart, and proceed to checkout. On the address selection page, you should be able to select both the parent and child addresses.
7. If any of the previously mentioned fields are not set, the address will not be shown at checkout. If no valid addresses are available, a warning message will be displayed and a contact form will be shown.
