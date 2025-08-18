1. **Create a Location for the Vehicle**
- Navigate to Inventory > Configuration > Locations and create a new location.
- Set a name.
- Set the `Parent Location` to `Vehicles`.
- Set the location type to `Internal Location`.
- Save the location.

2. **Create an FSM Vehicle**
- Navigate to Field Service > Master Data > Vehicles and create a new vehicle.
- Set a name.
- Assign a driver.
- Assign the location you created in step 1.
- Save the vehicle.
- Enter the driver's record and set the `Default Vehicle` field to the vehicle you just created.

3. **Generate Stock Moves**
- Navigate to Inventory > Operations > Transfers and create a new transfer.
- On the `Operation Type` field, select an operation type that supports FSM vehicle loading or unloading. Examples of this include `Vehicle Loading`, to load a vehicle from stock, and `Location Delivery`, to unload a vehicle to a customer location.
- Add the products you want to transfer and save the transfer.
- By default, the Source Location or Destination Location (depending on the selected operation type) will be set to the default `Vehicles` location.

4. **Validate the Transfer**
- In the `Additional Info` tab, set the FSM Vehicle on the transfer.
- If you link an FSM order to the transfer, and the FSM order has a vehicle assigned with a storage location that is a child of the `Vehicles` location, the vehicle and its corresponding location will be automatically set on the transfer.
- When validating the picking, the destination location of the picking and it's move lines will be updated to the vehicle's storage location. The assigned products will be moved from or to the vehicle location, depending on the selected operation type.
- If you try to confirm a transfer without setting the FSM Vehicle, an error will be raised.
- If you try to set a vehicle or link an FSM order with a vehicle whose storage location is not a child of the Vehicles location, an error will be raised.

Useful groups to manage this module:
- Technical / Manage Multiple Stock Locations
