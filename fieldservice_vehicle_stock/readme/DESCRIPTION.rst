This module is an add-on for the Field Service application in Odoo.
It allows you to establish stock locations for field service vehicles
and process stock moves with field service vehicles.

In field service operations, the general flow of inventory is as follows:
Stock Location -> Vehicle Location -> Customer Location

Initially there is a demand for product in the Customer Location, but we
are not sure which field service vehicle needs to load that product until
a field service order and vehicle is planned.

This module will automatically update pickings linked to field service orders
so that inventory is moved to the proper vehicle storage locations.
