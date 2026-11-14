# Field Service - Sale Stock Route

This module integrates `fieldservice_sale_stock`, `fieldservice_route`, and `fieldservice_availability`, enabling automatic creation and scheduling of FSM orders from sales orders with flexible route assignment and delivery time slot management.

## Confirmation of Sales Orders

When a sales order contains a product that generates an FSM order:
- An FSM location must be set on the sales order.
- Route assignment, FSM person, and route days are optional upon confirmation. If no route or driver is assigned, the order confirms flexibly and creates an unassigned FSM order in the pending orders pool.

## Operational Delivery Days Resolution

Operational days (allowed days of the week) are resolved dynamically via the 4-tier hierarchy in `get_allowed_route_days()`:
1. **Location Override**: Days selected directly on `fsm.location`.
2. **Route Default**: Days selected on the assigned `fsm.route`.
3. **Company Default**: Days configured in Field Service Settings (`res.company`).
4. **System Fallback**: All active `fsm.route.day` records in the system (Monday–Sunday).

## Automatic Scheduling and Delivery Time Ranges

The active delivery time range for any sale order is resolved using a 5-tier hierarchy from `fieldservice_availability`:
1. **Location Seasonal Schedule**: Active seasonal schedule on the location (day-specific grid or general seasonal hours).
2. **Location Default Schedule**: Default schedule on the location (day-specific grid or general default hours).
3. **Route Seasonal Schedule**: Active seasonal schedule on the assigned route (day-specific grid or general seasonal hours).
4. **Route Default Schedule**: Default schedule on the assigned route (day-specific grid or general default hours).
5. **Global Fallback**: Highest-priority global delivery time range (`fsm.delivery.time.range`).

This logic is applied universally upon order confirmation:
- **Unset Delivery Dates:** If `commitment_date` is empty, the system calculates the next valid operational day starting from tomorrow (evaluating Location ⟶ Route ⟶ Company Default Settings ⟶ All Active Days) and sets the start and end hours resolved from the schedule hierarchy.
- **Manual Delivery Dates:** If delivery dates are set manually, the system preserves the selected calendar day and standardizes start and end hours using the schedule hierarchy.
- **Route Validation & Force Schedule:** If a route is assigned, the delivery date is validated against the route's operational days. This validation can be overridden by enabling **Force Schedule** on the route.

## FSM Order Management

- **Postpone Delivery:** Users can postpone an FSM order to the next available operational delivery day directly from the FSM order header.
- **Bidirectional Date Synchronization:** Updating dates on an FSM order automatically synchronizes the corresponding sales order commitment dates and active stock pickings.