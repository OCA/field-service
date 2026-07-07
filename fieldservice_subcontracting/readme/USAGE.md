## Create the subcontract Purchase Order

1. Create or open a Field Service Order that uses a template configured for
   subcontracting.
2. Assign a worker.
3. Move the order to the stage configured to create the subcontract Purchase
   Order.

![Field Service Order buttons for subcontracting](../static/readme/fso_purchase_order_buttons.png)

1. The module resolves the vendor before creating the Purchase Order.
2. If the worker related partner has a parent company marked as subcontractor,
   the parent company is used as the vendor.
3. Otherwise, if the worker related partner is marked as subcontractor, that
   partner is used as the vendor.
4. If neither condition applies, the worker is considered internal and no
   Purchase Order is created. The Field Service Order chatter records that no
   Purchase Order was created for an internal worker.
5. Use the Purchase Order smart button to open the generated draft Purchase
   Order.
6. Review the Purchase Order. Its Expected Arrival is set from the Field Service
   Order Scheduled End (`scheduled_date_end`).
7. Confirm the Purchase Order manually.

![Field Service Order smart button on the Purchase Order](../static/readme/purchase_order_fso_button.png)

1. If the Purchase Order is not created, check the Field Service Order chatter.
2. Review the reason posted by the module.
3. Fix the missing configuration or worker data.
4. Move the order through the configured stage again if needed.

## Update the Purchase Order Expected Arrival

1. Change the Field Service Order planned dates.
2. Save the Field Service Order.
3. The active subcontract Purchase Order Expected Arrival is updated with the
   current Field Service Order Scheduled End (`scheduled_date_end`).
4. The generated Purchase Order line expected date is updated as well, so the
   Purchase Order header keeps the same Expected Arrival.

## Update delivered quantities

1. Log timesheet hours on the Field Service Order.
2. Move the Field Service Order to the stage configured to update subcontract
   delivered quantities.
3. The module updates the delivered quantity on the subcontract Purchase Order
   line with the total timesheet hours of the Field Service Order.
4. The ordered quantity remains unchanged after the Purchase Order is created.
5. Create the vendor bill after the delivered quantity has been updated when the
   product bills based on received quantities.

## Reassign or cancel an order

1. Use the Reassign Worker button when an order with at least one subcontract
   Purchase Order must be reassigned.
2. The Reassign Worker button remains available even if all linked subcontract
   Purchase Orders are cancelled.
3. The Reassign Worker button is only available while the Field Service Order is
   not in a closed stage.
4. If the Field Service Order is already in a closed stage, move it to a
   non-closed stage before reassigning the worker, if the business process
   allows it.
5. Select the new worker in the reassignment wizard.
6. Confirm the wizard.
7. The wizard cancels draft vendor bills linked to active subcontract Purchase
   Orders before cancelling those Purchase Orders.
8. The wizard cancels active subcontract Purchase Orders.
9. If the new worker is also a subcontractor, the module creates a new Purchase
   Order for that subcontractor.
10. To cancel a Field Service Order with active subcontract Purchase Orders, use
   the standard cancel action.
11. Choose whether to cancel only the Field Service Order or also its active
   subcontract Purchase Orders.
12. If there are posted vendor bills, manage the Purchase Orders and vendor
    bills manually before reassigning or cancelling the Field Service Order.
