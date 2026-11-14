To configure this module, you need to:

- Go to Inventory \> Configuration \> Routes
- Select the routes that you want to use from a FSM order
- Check the box 'FSM Order Line' for outbound transfer
- Check the box 'FSM Return Line' for inbound transfer

The route 'Receipt in 1 step' has no procurement rule so if you want
items to be returned from the service location to your warehouse, you
need to create a new procurement rule for that route:

- Name: YourCompany: Return
- Action: Move From Another Location
- Procurement Location: WH/Stock
- Served Warehouse: YourCompany
- Source Location: Partner Locations/Customers
- Move Supply Method: Take From Stock
- Operation Type: YourCompany: Receipts
