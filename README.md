
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/field-service&target_branch=17.0)
[![Pre-commit Status](https://github.com/OCA/field-service/actions/workflows/pre-commit.yml/badge.svg?branch=17.0)](https://github.com/OCA/field-service/actions/workflows/pre-commit.yml?query=branch%3A17.0)
[![Build Status](https://github.com/OCA/field-service/actions/workflows/test.yml/badge.svg?branch=17.0)](https://github.com/OCA/field-service/actions/workflows/test.yml?query=branch%3A17.0)
[![codecov](https://codecov.io/gh/OCA/field-service/branch/17.0/graph/badge.svg)](https://codecov.io/gh/OCA/field-service)
[![Translation Status](https://translation.odoo-community.org/widgets/field-service-17-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/field-service-17-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Field Service Management

[Field Service Management](https://en.wikipedia.org/wiki/Field_service_management) (FSM) coordinates company resources employed at, or en route to, client sites, rather than on the company's premises. FSM most commonly refers to companies who need to manage installation, service or repairs of systems or equipment.

Examples of field service use cases are:

- In telecommunications and cable industry, technicians who install cable or run phone lines into residences or business establishments.
- In healthcare, mobile nurses who provide in-home care for elderly or disabled.
- In gas utilities, engineers who are dispatched to investigate and repair suspected leaks.
- In heavy engineering, mining, industrial and manufacturing, technicians dispatched for preventative maintenance and repair.
- In property maintenance, including landscaping, irrigation, and home and office cleaning.
- In HVAC industry, technicians have the expertise and equipment to investigate units in residential, commercial and industrial environments.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[base_territory](base_territory/) | 17.0.1.0.0 | [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) [![brian10048](https://github.com/brian10048.png?size=30px)](https://github.com/brian10048) | This module allows you to define territories, branches, districts and regions to be used for Field Service operations or Sales.
[fieldservice](fieldservice/) | 17.0.1.1.0 | [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) [![brian10048](https://github.com/brian10048.png?size=30px)](https://github.com/brian10048) | Manage Field Service Locations, Workers and Orders
[fieldservice_account](fieldservice_account/) | 17.0.1.0.0 | [![osimallen](https://github.com/osimallen.png?size=30px)](https://github.com/osimallen) [![brian10048](https://github.com/brian10048.png?size=30px)](https://github.com/brian10048) [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Track invoices linked to Field Service orders
[fieldservice_account_analytic](fieldservice_account_analytic/) | 17.0.1.0.0 | [![osimallen](https://github.com/osimallen.png?size=30px)](https://github.com/osimallen) [![brian10048](https://github.com/brian10048.png?size=30px)](https://github.com/brian10048) [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Track analytic accounts on Field Service locations and orders
[fieldservice_calendar](fieldservice_calendar/) | 17.0.1.0.0 | [![hparfr](https://github.com/hparfr.png?size=30px)](https://github.com/hparfr) | Add calendar to FSM Orders
[fieldservice_crm](fieldservice_crm/) | 17.0.1.0.0 | [![patrickrwilson](https://github.com/patrickrwilson.png?size=30px)](https://github.com/patrickrwilson) | Create Field Service orders from the CRM
[fieldservice_isp_flow](fieldservice_isp_flow/) | 17.0.1.0.0 | [![osi-scampbell](https://github.com/osi-scampbell.png?size=30px)](https://github.com/osi-scampbell) | Field Service workflow for Internet Service Providers
[fieldservice_recurring](fieldservice_recurring/) | 17.0.1.0.0 | [![wolfhall](https://github.com/wolfhall.png?size=30px)](https://github.com/wolfhall) [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) [![brian10048](https://github.com/brian10048.png?size=30px)](https://github.com/brian10048) | Manage recurring Field Service orders
[fieldservice_route](fieldservice_route/) | 17.0.1.0.0 | [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | Organize the routes of each day.
[fieldservice_size](fieldservice_size/) | 17.0.1.0.0 | [![brian10048](https://github.com/brian10048.png?size=30px)](https://github.com/brian10048) | Manage Sizes for Field Service Locations and Orders
[fieldservice_stage_validation](fieldservice_stage_validation/) | 17.0.1.0.0 | [![brian10048](https://github.com/brian10048.png?size=30px)](https://github.com/brian10048) [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | Validate input data when reaching a Field Service stage
[fieldservice_stock](fieldservice_stock/) | 17.0.1.0.0 | [![brian10048](https://github.com/brian10048.png?size=30px)](https://github.com/brian10048) [![wolfhall](https://github.com/wolfhall.png?size=30px)](https://github.com/wolfhall) [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) [![smangukiya](https://github.com/smangukiya.png?size=30px)](https://github.com/smangukiya) | Integrate the logistics operations with Field Service
[fieldservice_vehicle](fieldservice_vehicle/) | 17.0.1.0.0 | [![wolfhall](https://github.com/wolfhall.png?size=30px)](https://github.com/wolfhall) [![max3903](https://github.com/max3903.png?size=30px)](https://github.com/max3903) | Manage Field Service vehicles and assign drivers

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
