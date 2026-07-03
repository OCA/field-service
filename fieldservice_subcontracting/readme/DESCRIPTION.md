This module integrates Field Service with Purchasing to automate the
subcontracting workflow.

It allows users to:

1. Mark subcontractor vendors on partners.
2. Configure a service product on Field Service order templates.
3. Resolve the Purchase Order vendor from the assigned worker or its parent
   company.
4. Create draft Purchase Orders for subcontracted orders.
5. Set the Purchase Order Expected Arrival from the Field Service Order
   Scheduled End.
6. Keep the Purchase Order Expected Arrival synchronized when the Field Service
   Order planned dates change.
7. Update delivered quantities from Field Service timesheets.
8. Reassign workers on orders with linked subcontract Purchase Orders.

The module uses `fieldservice_stage_server_action` to trigger automation on
stage transitions.
