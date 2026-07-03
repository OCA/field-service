1. Field Service operations sometimes require external workers or companies to
   perform part of the service delivery.
2. A Field Service Order can be assigned to an internal worker, an individual
   subcontractor, or an employee of a subcontractor company.
3. The module resolves the Purchase Order vendor from the assigned worker:
   when the worker partner has a subcontractor parent company, that parent
   company receives the Purchase Order; otherwise, the worker partner receives
   it when it is marked as subcontractor.
4. If neither the worker partner nor its parent company is marked as
   subcontractor, the worker is treated as internal and no Purchase Order is
   created.
5. The company can create a Purchase Order for that external service without
   manually duplicating information between Field Service and Purchase.
6. The Purchase Order Expected Arrival is set from the Field Service Order
   Scheduled End (`scheduled_date_end`).
7. When the Field Service Order planned dates change, the linked subcontract
   Purchase Order Expected Arrival is updated to match the current Scheduled
   End.
8. The Purchase Order remains under the standard Odoo purchase flow: it is
   created as a draft, reviewed and confirmed manually, and later billed by the
   vendor.
9. Timesheet hours logged on the Field Service Order can be pushed to the
   Purchase Order line as delivered quantity.
10. Vendor bills based on received quantities can then be created with the
   correct quantity.
11. Worker reassignment is available for orders with at least one linked
   subcontract Purchase Order, even if all linked subcontract Purchase Orders
   are cancelled.
12. Worker reassignment is only available before the Field Service Order reaches
   a closed stage.
