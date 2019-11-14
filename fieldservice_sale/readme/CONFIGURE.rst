Products must be configured properly in order to create field service
orders upon sale order confirmation.

The field service policy of a product defines how it generates a field service
order if the product is sold via sale order.

To configure a product that generates a unique field service order on each
sale order line:

* Go to Sales > Catalog > Products
* Create or select a product
* Set the Product Type to 'Service' under General Information tab
* Set the Field Service Policy to 'Per Sale Order Line'
* Under Invoicing tab, set the Field Service Tracking option
* Select the FSM Order Template that will be used for creating FSM Orders when
  a Sale Order is confirmed with this product

To configure a product that generates a unique field service order for
an individual sale order:

* Go to Sales > Catalog > Products
* Create or select a product
* Set the Field Service Policy to 'Per Sale Order'

To setup a sales territory:

* Go to Field Service > Master Data > Locations
* Create or select a location
* Go to the Sales tab and select the sales territory
