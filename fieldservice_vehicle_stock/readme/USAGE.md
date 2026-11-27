1. **Create a Location for the Vehicle**
   - Navigate to Inventory > Configuration > Locations and create a new
     location.
   - Set a name.
   - Set the Parent Location to Vehicles.
   - Set the location type to Internal Location.
   - Save the location.
2. **Create an FSM Vehicle**
   - Navigate to Field Service > Master Data > Vehicles and create a new
     vehicle.
   - Set a name.
   - Assign a driver.
   - Assign the location you created in step 1.
   - Save the vehicle.
   - Open the driver's record and set the Default Vehicle field to the
     vehicle you just created.
3. **Generate Stock Moves**
   - Navigate to Inventory > Operations > Transfers and create a new
     transfer.
   - On the Operation Type field, select an operation type that supports
     FSM vehicle loading or unloading, for example Vehicle Loading (from
     stock to a vehicle) or Location Delivery (from a vehicle to a customer
     location).
   - Add the products you want to transfer and save the transfer.
   - By default, the Source Location or Destination Location (depending on
     the operation type) is the Vehicles location.
4. **Validate the Transfer**
   - In the Additional Info tab, set the FSM Vehicle on the transfer.
   - A transfer linked to an FSM order takes the vehicle of that order, and
     follows it when the vehicle of the order changes.
   - When reserving or validating the transfer, its destination (loading)
     or source (unloading) location and its move lines are set to the
     vehicle storage location.
   - Reserving or validating a transfer of these operation types without a
     vehicle raises an error, as does a vehicle whose storage location is
     not a descendant of the Vehicles location.

Useful groups to manage this module:

- Technical / Manage Multiple Stock Locations
