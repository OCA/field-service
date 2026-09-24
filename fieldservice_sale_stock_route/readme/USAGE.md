# Field Service - Sale Stock Route Usage

## Configuration

Before creating sales orders, configure delivery schedules and operational days:

1. **Company Default Operational Days:** Navigate to **Field Service > Configuration > Settings**. Scroll to the **Routes** section and select your standard company operational days (e.g., Monday through Friday). These apply as the baseline when no route or location overrides are defined.
2. **Global Fallback Schedules:** Navigate to **Field Service > Configuration > Availability > Global Delivery Time Ranges** to configure fallback hours (e.g., `07:00` to `15:00`).
3. **Route Delivery Schedules:** Navigate to **Field Service > Master Data > Routes**. Select a route to configure its allowed operational days, default schedule hours (`has_default_schedule`), or seasonal schedule hours (`has_seasonal_schedule`).
4. **Location Delivery Schedules:** Navigate to **Field Service > Master Data > Locations**. Select a location and navigate to the **Delivery Schedule** tab to configure location-specific operational days or custom default/seasonal schedule hours.

---

## Operating Flow

1. Navigate to **Sales > Orders** and create a new sales order.
2. Select the **Customer** and **FSM Location**.
3. Add a product configured with Field Service tracking (`field_service_tracking` set to create an FSM order).
4. In the **Other Info** tab, set the **Delivery Date** (`commitment_date`), or leave it empty:
   - If left empty, the system automatically finds the next valid operational delivery day starting from tomorrow, resolving operational days through the hierarchy (Location Override ⟶ Route Default ⟶ Company Default Settings ⟶ All Active Days).
   - If set manually, the system preserves the selected calendar date.
   - In both cases, start and end hours are standardized using the 5-tier delivery schedule hierarchy (Location Seasonal ⟶ Location Default ⟶ Route Seasonal ⟶ Route Default ⟶ Global Fallback).
5. Click **Confirm**.
   - If an assigned route has restricted operational days, the system validates the selected date against allowed route days unless **Force Schedule** is enabled on the route.
   - If no route nor person is assigned, the order confirms and creates an unassigned FSM order in the pending orders pool.
6. Open the generated **FSM Order**:
   - Schedule details (`scheduled_date_start` and `scheduled_date_end`) reflect the delivery dates computed from the sales order.
   - Click **Postpone Delivery** in the header to reschedule the order to the next available operational delivery day.
   - Updating schedule dates on the FSM order automatically updates the sales order commitment dates and open stock pickings.