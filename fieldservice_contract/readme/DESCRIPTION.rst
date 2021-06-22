This module allows to manage field services orders and recurring orders from contract.

Features:
* FSM orders are linked to invoices based on the invoice period
* FSM recurring orders' end date is tied to contract line end's date.
* Quantity on invoice line can be constant or based on the number of FSM orders within the period.


Example of workflow:

A sale order, when confirmed, creates a contract.
The contract creates field services recurring orders and manage the invoicing.


Why use sale order:
In order to benefit from other apps (CRM), and features of sales (sale exceptions, sale workflow, etc.)

Why use contract:
In order to manage the recurring invoicing and benefit from features like reconduction, etc.
