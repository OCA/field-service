To configure this module, you need to:

* Go to Field Service > Master Data > Locations
* Create or select a location and set the inventory location

If you are in a multi-warehouse situation:

* Go to Field Service > Configuration > Territories
* Create or select a territory
* Set the warehouse that will serve this territory

Products can be automatically converted into FSM Equipments.
This is only available only for products tracked by serial number.
This needs to be enabled both on Operation Types and Products.
For example, we may want to create the FSM Equipment on Delivery,
or on Receipts.

To enable on Products:

* Go to Inventory > Master Data > Products
* Open the Product form, Inventory tab
* On the "Traceability" section, make sure
  "Tracking" is set to "By Unique Serial Number"
* Enable the "Creates FSM Equipment" checkbox

To enable on Operation Types:

* Go to Inventory > Configuration > Operation Types
* Select the intended Operation Type ("Receipts" for example)
* On the "Traceability" section, enable the
  "Create FSM Equipment" checkbox
