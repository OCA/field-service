# Field Service Availability

## 1. Configuring Company Default Operational Days

1. Navigate to **Field Service > Configuration > Settings**.
2. Scroll to the **Routes** section.
3. In the **Default Operational Days** field, select the standard working days for your company (e.g., Monday through Friday). These days will apply to all locations and routes automatically unless specifically overridden.

## 2. Configuring Global Fallback Schedules

1. Navigate to **Field Service > Configuration > Availability > Global Delivery Time Ranges**.
2. Click **New** to create a fallback time range.
3. Set the **Start Time** and **End Time** (e.g., `07:00` to `15:00`). Hours must strictly be between `00:00` and `23:59`.
4. Adjust the **Sequence** to ensure your primary fallback is at the top of the list.

## 3. Assigning Schedules to Routes

1. Navigate to **Field Service > Master Data > Routes**.
2. Select a route and navigate to the **Route Delivery Schedule** section.
3. **Operational Days:** Override the company default by selecting specific allowed days for this route.
4. **Default Schedule:** Enable `Has custom default schedule` to define standard working hours (e.g., `08:00` to `16:00`). You can also differentiate hours by specific days of the week.
5. **Seasonal Schedule:** Enable `Has seasonal schedule` to define temporary overriding hours (e.g., Summer hours from June 1 to Sept 30).

## 4. Assigning Schedules to Locations (Customer Specific)

1. Navigate to **Field Service > Master Data > Locations**.
2. Select a location and navigate to the **Delivery Schedule** tab.
3. Set specific **Operational Days** or custom schedules for this location. Any schedule assigned directly to the location will strictly override the route-level and company-level defaults.

## 5. Configuring Blackout and Stress Days

1. Navigate to **Field Service > Configuration > Availability**.
2. Select **Blackout Days**, **Blackout Groups**, or **Stress Days** to add operational exceptions or demand surges to specific calendar dates.

## 🧪 Developer Testing / Validation

To verify schedule resolution is working as expected from the Odoo shell or custom code:

```python
location = env["fsm.location"].browse(1)

# Get the allowed operational days for the location
# Evaluates hierarchy: Location -> Route -> Company Setting -> All Active Days
allowed_days = location.get_allowed_route_days()

# Get the exact delivery hours (start, end) for a specific date
# Evaluates hierarchy: Loc Seasonal -> Loc Default -> Route Seasonal -> Route Default -> Global
hours = location.get_delivery_time_ranges(target_date="2026-07-15")
```
