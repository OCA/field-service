# Field Service Availability

This module defines blackout days (non-operational days), blackout groups, stress days (high-demand periods), and delivery time ranges for field service operations. It provides the necessary models and hierarchical resolution methods used by other modules to manage scheduling, availability, and workload adjustments.

## Core Concepts

- **Blackout Days (`fsm.blackout.day`)**: Represent specific dates when field service operations are unavailable (e.g., holidays, company-wide closures).
- **Blackout Groups (`fsm.blackout.group`)**: Allow grouping blackout days by geographical regions or postal codes (ZIPs).
- **Stress Days (`fsm.stress.day`)**: Indicate dates with increased service demand (e.g., peak business periods requiring additional workforce).
- **Global Delivery Time Ranges (`fsm.delivery.time.range`)**: Reusable global fallback schedules defining available time slots for field service operations when no specific location or route schedule exists.

## Hierarchical Schedule Resolution

Delivery schedules are managed directly on **Locations** (`fsm.location`) and **Routes** (`fsm.route`) via a comprehensive inline configuration. When requesting the active delivery schedule for a location on a specific date, the system resolves the active time window using a strict 5-tier hierarchy:

1. **Location Seasonal Schedule**: Active recurring date window on the target date (allows day-specific overrides).
2. **Location Default Schedule**: Year-round default schedule assigned to the location (allows day-specific overrides).
3. **Route Seasonal Schedule**: Active recurring date window on the target date assigned to the location's route.
4. **Route Default Schedule**: Year-round default schedule assigned to the location's route.
5. **Global Fallback**: The highest-priority active global delivery time range in the system.

## Operational Delivery Days

Operational days (e.g., Monday-Friday) are resolved seamlessly through the following hierarchy:

1. **Location Override**: Days selected directly on `fsm.location`.
2. **Route Default**: Days selected on the assigned `fsm.route`.
3. **Company Default**: Days selected in the Field Service Global Settings (`res.company`).
4. **System Fallback**: If none of the above are set, defaults to all active `fsm.route.day` records in the system (Monday–Sunday).

*Note: This is a technical base module. Extend this module to integrate availability management into field service sale and stock workflows.*
