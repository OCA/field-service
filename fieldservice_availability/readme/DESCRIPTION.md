This module defines blackout days (non-operational days), stress days
(high-demand periods), and delivery time ranges for field service
operations. It provides the necessary models to store this information,
which can be used by other modules to manage scheduling, availability,
and workload adjustments.

- **Blackout Days (\`fsm.blackout.day\`)**: Represent dates when field
  service operations are unavailable (e.g., holidays, company-wide
  closures).
- **Blackout Groups (\`fsm.blackout.group\`)**: Represent groups of days when field
  service operations are unavailable (e.g., holidays, company-wide
  closures).
- **Stress Days (\`fsm.stress.day\`)**: Indicate dates with increased
  service demand (e.g., peak business periods requiring additional
  workforce).
- **Delivery Time Ranges (\`fsm.delivery.time.range\`)**: Define
  available time slots for scheduling field service operations.
- **Restricts blackout days for Scheduled Start (ETA) orders with the same date**

This module validates Scheduled Start (ETA) dates on field service orders
against blackout days configured on their route. Orders with an ETA that
falls on a matching blackout day cannot be saved.
