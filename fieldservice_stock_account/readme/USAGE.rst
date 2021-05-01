To use this module, you need to:

* Go to Field Service
* Create an order for a customer location (type of the inventory location must be 'Customer')
* Add inventory items and process them. Their delivery will generate an accounting entry.
* Complete the field service order
* Add some contractor costs or timesheet entries depending on the worker (vendor or employee)
* In the accounting tab, click on "Create invoice". The delivered inventory items will be added to the customer invoice with a 0$ price unit and they will not show up in the PDF report of the invoice.

    * Go to Invoicing > Customers > Invoices
    * Validate the invoice.
    * Check the accounting entry to make sure the value of the inventory items is accounted as a cost of goods/services sold.

* Repeat the process but in the accounting tab, click on "No invoice"

    * Go to Invoicing > Customers > Invoices
    * Open the invoice related to the field service order
    * Check that the invoice has a 0$ total and is paid
    * Check the accounting entry to make sure the value of the inventory items is accounted as a cost of goods/services sold.
