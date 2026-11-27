To configure this module, you need to:

## Configure Operation Types for Loading FSM Vehicles

Specific stock operation types can be configured for moving inventory to
the storage locations of FSM Vehicles. Moves will not be processed if the
FSM Vehicle is not set on the transfers of these operation types.

1. Go to Inventory > Configuration > Operation Types.
2. Select or create an Operation Type.
3. Check the box "Used to load a Field Service Vehicle" (or "Used to unload
   a Field Service Vehicle").

## Verify procurement routes

Some new procurement routes are added with this module. Check that these
routes fit your individual business needs or create new ones.

Be sure to have a rule that uses an Operation Type configured for FSM
Vehicle loading, and that the rule has a Destination Location which is a
parent of the FSM Vehicle inventory location.

## Configure FSM Vehicles

Each FSM Vehicle that will carry inventory needs a stock inventory location.
Individual vehicle inventory locations must be descendants of the Vehicles
location.

1. Go to Field Service > Master Data > Vehicles.
2. Select or create a Field Service Vehicle.
3. Set the desired Inventory Location for that vehicle.

## Access rights

Field Service users can create and change the transfers of the operation
types that load or unload a vehicle. Other transfers stay read-only for them,
unless another access right (Inventory, Sales, Purchase...) lets them change
transfers.
