This module defines blackout days (non-operational days), blackout groups, stress days (high-demand periods), and delivery time ranges for field service operations. It provides the necessary models and hierarchical resolution methods used by other modules to manage scheduling, availability, and workload adjustments.

- **Blackout Days (`fsm.blackout.day`)**: Represent specific dates when field service operations are unavailable (e.g., holidays, company-wide closures).
- **Blackout Groups (`fsm.blackout.group`)**: Allow grouping blackout days by geographical regions or postal codes (ZIPs).
- **Stress Days (`fsm.stress.day`)**: Indicate dates with increased service demand (e.g., peak business periods requiring additional workforce).
- **Delivery Time Ranges (`fsm.delivery.time.range`)**: Reusable master schedules defining available time slots for field service operations. Time ranges can be defined as **Default** (year-round) or **Seasonal** (recurring date intervals with start/end month and day).

### Hierarchical Schedule Resolution
Delivery time ranges are linked via `Many2many` relationships to Locations (`fsm.location`) and Routes (`fsm.route`). When requesting the active delivery schedule for a location on a specific date, the system resolves the active time window using the following hierarchy:
1. **Location Seasonal Schedule**: Active recurring date window on the target date assigned to the location.
2. **Location Default Schedule**: Year-round default schedule assigned to the location.
3. **Route Seasonal Schedule**: Active recurring date window on the target date assigned to the location's route.
4. **Route Default Schedule**: Year-round default schedule assigned to the location's route.
5. **Global Fallback**: Default system-wide delivery time range.

This is a technical module and does not provide standalone order processing on its own. Extend this module to integrate availability management into field service sale and stock workflows.