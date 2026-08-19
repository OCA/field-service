# Field Service Customer Journey

This document describes the reusable portal journey demonstrated with solar installation and equipment-service data. Links use the public URL configured in Odoo through `web.base.url`.

## Roles

| Role | Responsibility |
|---|---|
| Customer | Request a survey, approve quotations, schedule installation, and request service |
| Coordinator | Review requests, prepare quotations, assign routes, and monitor work |
| Technician | Perform surveys, installations, maintenance, and repairs |

## Stable Workflow Configuration

Customer behavior is controlled by technical fields rather than translated record names:

| Record | Technical field | Values |
|---|---|---|
| FSM order type | `service_type` | `survey`, `installation`, `maintenance`, `repair`, `other` |
| Sale order template | `service_type` | `survey`, `installation`, `maintenance`, `repair`, `other` |
| FSM stage | `notification_event` | `none`, `started`, `completed` |
| FSM route | `route_type` | `visit`, `installation`, `maintenance` |

Labels can be translated or renamed without changing workflow behavior.

## Journey

1. The customer opens `/my/visit` and submits a site-survey request.
2. Odoo creates the customer location, CRM opportunity, and survey quotation from configured templates.
3. The coordinator schedules and assigns the survey work order.
4. Completing the survey enables preparation of the installation quotation.
5. After confirmation and payment, the customer chooses an installation slot at `/my/installation/<sale_order_id>`.
6. The technician completes installation and records the installed panels, inverter, batteries, and related equipment at the FSM location.
7. Locations with installed equipment become available at `/my/requests`.
8. The customer requests preventive maintenance or repair against the installed location.

## Notifications

The general portal sends email using dynamic company identity, configured public URLs, and sale-order currency formatting. External messaging is optional and supplied by a separate integration bridge. Notification failures are logged and do not roll back operational state changes.

## Required Settings

- Public base URL
- Site-survey CRM team
- Site-survey sale order template
- Maintenance sale order template
- Routes and daily capacity
- Order types with stable service purposes
- Stages with stable notification events

## Security

Portal users may access only their own sale orders, FSM locations, installed equipment, and work orders. Maintenance requests require an accessible location with installed equipment.
