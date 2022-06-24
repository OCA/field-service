To configure this module, you need to:

# Configure Operation Types for Loading FSM Vehicles
Specific stock operation types can be configured for
moving inventory to the storage locations of FSM Vehicles.
Moves will not be processed if the FSM Vehicle is not set on
the transfers of these operation types.
#. Go to Inventory > Configuration > Operation Types
#. Select or Create an Operation Type
#. Check the box "Used to Load a Field Service Vehicle"

# Verify procurement routes
Some new procurement routes are added with this module. Check
that these routes fit your individual business needs or you can
create new ones.

Be sure to have a rule that utilizes an Operation Type that is
configured for FSM Vehicle Loading and the rule has a Destination
Location which is a parent of the FSM Vehicle inventory location

# Configure FSM Vehicles
Each FSM Vehicle that will carry inventory needs to have a
stock inventory location.  Individual vehicle inventory
locations should be a descendant location of a procurement
rule's Destination Location.
#. Go to Field Service > Master Data > Vehicles
#. Select or Create a Field Service Vehicle
#. Set the desired Inventory Location for that vehicle
