# Copyright (C) 2026 Gray Matter Logic
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time, timedelta

from pytz import timezone, utc

from odoo import api, fields, models

# west, south, east, north — disjoint boxes over the Phoenix metro.
ROUTES = [
    ("Central Phoenix", (-112.11, 33.43, -112.03, 33.50)),
    ("Scottsdale", (-111.96, 33.48, -111.86, 33.55)),
    ("Tempe", (-111.97, 33.39, -111.89, 33.45)),
    ("Glendale", (-112.24, 33.52, -112.16, 33.60)),
    ("Mesa", (-111.88, 33.38, -111.76, 33.46)),
]

# name, street, city, zip, latitude, longitude
CUSTOMERS = [
    (
        "Sonoran Facilities",
        "2 N Central Ave",
        "Phoenix",
        "85004",
        33.4489,
        -112.0742,
    ),
    (
        "Camelback Property Group",
        "7373 E Doubletree Ranch Rd",
        "Scottsdale",
        "85258",
        33.5652,
        -111.9224,
    ),
    (
        "Salt River Services",
        "455 N Mill Ave",
        "Tempe",
        "85281",
        33.4294,
        -111.9401,
    ),
    (
        "West Valley Maintenance",
        "7550 W Glendale Ave",
        "Glendale",
        "85303",
        33.5386,
        -112.2204,
    ),
    (
        "Desert Commercial Care",
        "100 N Center St",
        "Mesa",
        "85201",
        33.4156,
        -111.8312,
    ),
]

LOCATIONS = [
    ("Chase Field", "401 E Jefferson St", "Phoenix", "85004", 33.4455, -112.0668),
    (
        'Washington Street Plant',
        '201 E Washington St',
        'Phoenix',
        '85004',
        33.4486,
        -112.0715,
    ),
    ("Heard Museum", "2301 N Central Ave", "Phoenix", "85004", 33.4732, -112.0736),
    (
        'State Capitol Complex',
        '1700 W Washington St',
        'Phoenix',
        '85007',
        33.4484,
        -112.0968,
    ),
    (
        'Encanto Park Office',
        '2121 W Encanto Blvd',
        'Phoenix',
        '85009',
        33.4748,
        -112.1025,
    ),
    (
        'Fashion Square',
        '7014 E Camelback Rd',
        'Scottsdale',
        '85251',
        33.5022,
        -111.929,
    ),
    (
        'Old Town Scottsdale',
        '4248 N Scottsdale Rd',
        'Scottsdale',
        '85251',
        33.4968,
        -111.9262,
    ),
    (
        'Civic Center',
        '3939 N Drinkwater Blvd',
        'Scottsdale',
        '85251',
        33.4936,
        -111.9208,
    ),
    (
        'Indian Bend Yard',
        '7301 E Indian Bend Rd',
        'Scottsdale',
        '85250',
        33.538,
        -111.923,
    ),
    ("Hayden Road Shop", "4800 N Hayden Rd", "Scottsdale", "85251", 33.5088, -111.9095),
    ("Sun Devil Stadium", "500 E Veterans Way", "Tempe", "85281", 33.4262, -111.9335),
    ("Rio Salado Plant", "60 E Rio Salado Pkwy", "Tempe", "85281", 33.4318, -111.9398),
    ("Tempe Town Lake", "2000 E Rio Salado Pkwy", "Tempe", "85281", 33.4302, -111.9042),
    ("University Drive", "120 W University Dr", "Tempe", "85281", 33.4216, -111.9412),
    ("Apache Boulevard", "1900 E Apache Blvd", "Tempe", "85281", 33.4148, -111.9070),
    (
        'Glendale Avenue Shop',
        '5850 W Glendale Ave',
        'Glendale',
        '85301',
        33.5387,
        -112.1862,
    ),
    (
        'Northern Avenue Plant',
        '5605 W Northern Ave',
        'Glendale',
        '85301',
        33.5528,
        -112.1805,
    ),
    (
        '55th Avenue Warehouse',
        '6670 N 55th Ave',
        'Glendale',
        '85301',
        33.5345,
        -112.174,
    ),
    (
        'Thunderbird Road',
        '4960 W Thunderbird Rd',
        'Glendale',
        '85306',
        33.5755,
        -112.1685,
    ),
    ("Olive Avenue Yard", "7700 W Olive Ave", "Peoria", "85345", 33.5675, -112.2210),
    ("Mesa Main Street", "20 E Main St", "Mesa", "85201", 33.4152, -111.8310),
    ("Center Street Plant", "120 N Center St", "Mesa", "85201", 33.4188, -111.8302),
    (
        'University Drive Mesa',
        '535 W University Dr',
        'Mesa',
        '85201',
        33.4225,
        -111.8455,
    ),
    ("Greenfield Road", "1445 S Greenfield Rd", "Mesa", "85206", 33.3980, -111.7880),
    (
        'Country Club Drive',
        '1855 N Country Club Dr',
        'Mesa',
        '85201',
        33.451,
        -111.8395,
    ),
]

WORKERS = [
    ("Maria Lopez", "510 W Mariposa St", "Phoenix", "85013", 33.5152, -112.0835),
    ("Daniel Brooks", "1515 W Missouri Ave", "Phoenix", "85015", 33.5138, -112.0942),
    ("Priya Shah", "4025 N 7th Ave", "Phoenix", "85013", 33.5184, -112.0788),
    ("James Patel", "10801 N 78th St", "Scottsdale", "85260", 33.5822, -111.9104),
    ("Emily Carter", "7320 E Gold Dust Ave", "Scottsdale", "85258", 33.5684, -111.9226),
    (
        'Noah Bennett',
        '8501 E Via de Ventura',
        'Scottsdale',
        '85258',
        33.5621,
        -111.8984,
    ),
    ("Alicia Nguyen", "910 W Southern Ave", "Tempe", "85282", 33.3724, -111.9452),
    ("Omar Haddad", "1215 W Baseline Rd", "Tempe", "85283", 33.3782, -111.9584),
    ("Hannah Kim", "2100 S Mill Ave", "Tempe", "85282", 33.3686, -111.9402),
    ("Robert Hale", "9102 W Camelback Rd", "Glendale", "85305", 33.5094, -112.2552),
    ("Luis Ortega", "6808 N 91st Ave", "Glendale", "85305", 33.5322, -112.2558),
    ("Megan Clark", "10220 W Glendale Ave", "Glendale", "85307", 33.5384, -112.2754),
    ("Sofia Ramirez", "4120 E Main St", "Mesa", "85205", 33.4154, -111.7402),
    ("Ethan Wright", "1840 S Val Vista Dr", "Mesa", "85204", 33.4052, -111.7554),
    ("Chloe Martin", "355 N Power Rd", "Mesa", "85205", 33.4204, -111.6852),
]

CONTACTS = [
    "Alex Rivera",
    "Jordan Blake",
    "Sam Patel",
    "Riley Chen",
    "Casey Morgan",
    "Taylor Brooks",
    "Quinn Adams",
    "Avery Diaz",
    "Reese Cooper",
    "Drew Sanders",
    "Skyler Nguyen",
    "Parker Hayes",
    "Rowan Price",
    "Emerson Ward",
    "Finley Ross",
    "Sawyer Bennett",
    "Harper Cole",
    "Blake Foster",
    "Cameron Reyes",
    "Dakota Hughes",
    "Elliot Gray",
    "Frankie Long",
    "Glen Powell",
    "Hayden Cruz",
    "Indigo Walsh",
]

TASKS = [
    "HVAC inspection",
    "Filter replacement",
    "Electrical safety check",
    "Plumbing service",
    "Preventive maintenance",
]
STOP_HOURS = [8, 9.5, 11, 13, 14.5]
WORKERS_PER_ROUTE = 3
LOCATIONS_PER_ROUTE = 5
ORDERS_PER_DAYROUTE = 5
DAYROUTES_PER_ROUTE = 6


class FSMRoute(models.Model):
    _inherit = "fsm.route"

    @api.model
    def load_phoenix_demo(self):
        """Replace demo field service data with a complete Phoenix, AZ set.

        Orders and day routes are dated on weekdays inside the 20 days
        that follow installation.
        """
        country = self.env.ref("base.us")
        state = self.env["res.country.state"].search(
            [("code", "=", "AZ"), ("country_id", "=", country.id)], limit=1
        )
        team = self.env["fsm.team"].search(
            [("company_id", "in", (self.env.company.id, False))],
            order="sequence",
            limit=1,
        )
        if not team:
            team = self.env["fsm.team"].create({"name": "Phoenix Field Service"})
        weekdays = self.env["fsm.route.day"].browse(
            [
                self.env.ref(f"fieldservice_route.fsm_route_day_{index}").id
                for index in range(5)
            ]
        )
        dates = self._phoenix_dates()
        customers = self._ensure_records(
            "res.partner",
            ["fieldservice.test_partner"],
            "phoenix_customer",
            [
                self._phoenix_address(
                    country, state, item[1], item[2], item[3], item[4], item[5],
                    name=item[0],
                    is_company=True,
                    phone=f"602-555-{100 + index:04d}",
                    email=self._phoenix_email(item[0]),
                )
                for index, item in enumerate(CUSTOMERS)
            ],
        )
        contacts = self._ensure_records(
            "res.partner",
            [],
            "phoenix_contact",
            [
                {
                    "name": name,
                    "parent_id": customers[index // LOCATIONS_PER_ROUTE].id,
                    "is_company": False,
                    "type": "contact",
                    "phone": f"602-555-{200 + index:04d}",
                    "email": self._phoenix_email(name),
                }
                for index, name in enumerate(CONTACTS)
            ],
        )
        workers = self._ensure_records(
            "fsm.person",
            [
                "fieldservice.person_1",
                "fieldservice.person_2",
                "fieldservice.person_3",
                "fieldservice.test_person",
            ],
            "phoenix_worker",
            [
                self._phoenix_address(
                    country, state, item[1], item[2], item[3], item[4], item[5],
                    name=item[0],
                    phone=f"602-555-{300 + index:04d}",
                    mobile=f"602-555-{400 + index:04d}",
                    email=self._phoenix_email(item[0]),
                    team_id=team.id,
                )
                for index, item in enumerate(WORKERS)
            ],
            leftovers=True,
        )
        routes = self._ensure_records(
            "fsm.route",
            [
                "fieldservice_route.route_demo_north",
                "fieldservice_route.route_demo_south",
            ],
            "phoenix_route",
            [
                {
                    "name": name,
                    "fsm_person_id": workers[index * WORKERS_PER_ROUTE].id,
                    "max_order": 10,
                    "day_ids": [(6, 0, weekdays.ids)],
                }
                for index, (name, _box) in enumerate(ROUTES)
            ],
            leftovers=True,
        )
        for route_index, route in enumerate(routes):
            group = workers[
                route_index * WORKERS_PER_ROUTE : (route_index + 1) * WORKERS_PER_ROUTE
            ]
            group.write({"preferred_route_id": route.id})
        locations = self._ensure_records(
            "fsm.location",
            [
                "fieldservice.location_1",
                "fieldservice.location_2",
                "fieldservice.location_3",
                "fieldservice.test_location",
            ],
            "phoenix_location",
            [
                self._phoenix_address(
                    country, state, item[1], item[2], item[3], item[4], item[5],
                    name=item[0],
                    phone=f"602-555-{500 + index:04d}",
                    email=self._phoenix_email(item[0]),
                    owner_id=customers[index // LOCATIONS_PER_ROUTE].id,
                    contact_id=contacts[index].id,
                    fsm_route_id=routes[index // LOCATIONS_PER_ROUTE].id,
                    direction="<p>Check in at the front desk.</p>",
                    ref=f"PHX-{index + 1:02d}",
                )
                for index, item in enumerate(LOCATIONS)
            ],
            leftovers=True,
        )
        for route, (_name, box) in zip(routes, ROUTES):
            route.write({"area_shape": self._phoenix_area_wkt(*box)})
        self._phoenix_preferred_locations(workers, locations)
        self._phoenix_orders(routes, workers, locations, dates, team)
        return True

    @api.model
    def _phoenix_dates(self):
        today = fields.Date.context_today(self)
        weekdays = [
            today + timedelta(days=offset)
            for offset in range(20)
            if (today + timedelta(days=offset)).weekday() < 5
        ]
        picked = []
        for step in range(DAYROUTES_PER_ROUTE):
            if len(weekdays) == 1:
                index = 0
            else:
                index = round(step * (len(weekdays) - 1) / (DAYROUTES_PER_ROUTE - 1))
            day = weekdays[min(index, len(weekdays) - 1)]
            if day not in picked:
                picked.append(day)
        for day in weekdays:
            if len(picked) >= DAYROUTES_PER_ROUTE:
                break
            if day not in picked:
                picked.append(day)
        return picked

    @api.model
    def _phoenix_address(
        self, country, state, street, city, zipcode, latitude, longitude, **extra
    ):
        values = {
            "street": street,
            "city": city,
            "zip": zipcode,
            "state_id": state.id,
            "country_id": country.id,
            "partner_latitude": latitude,
            "partner_longitude": longitude,
            "tz": "America/Phoenix",
        }
        values.update(extra)
        return values

    @api.model
    def _phoenix_email(self, name):
        local = name.lower().replace(" ", ".")
        return f"{local}@example.com"

    @api.model
    def _phoenix_area_wkt(self, west, south, east, north):
        wkt = (
            f"POLYGON(({west} {south}, {east} {south}, {east} {north}, "
            f"{west} {north}, {west} {south}))"
        )
        self.env.cr.execute(
            "SELECT ST_AsText(ST_Transform(ST_GeomFromText(%s, 4326), 3857))",
            (wkt,),
        )
        return self.env.cr.fetchone()[0]

    @api.model
    def _phoenix_at(self, day, hour):
        hours = int(hour)
        minutes = int(round((hour - hours) * 60))
        local = timezone("America/Phoenix").localize(
            datetime.combine(day, time(hours, minutes))
        )
        return local.astimezone(utc).replace(tzinfo=None)

    def _phoenix_preferred_locations(self, workers, locations):
        links = self.env["fsm.location.person"].search(
            [("person_id", "in", workers.ids)]
        )
        links.unlink()
        vals_list = []
        for route_index in range(len(ROUTES)):
            route_locations = locations[
                route_index * LOCATIONS_PER_ROUTE : (route_index + 1)
                * LOCATIONS_PER_ROUTE
            ]
            group = workers[
                route_index * WORKERS_PER_ROUTE : (route_index + 1) * WORKERS_PER_ROUTE
            ]
            for person_index, person in enumerate(group):
                if person_index == 0:
                    preferred = route_locations
                else:
                    start = (person_index - 1) * 2
                    preferred = route_locations[start : start + 2]
                for sequence, location in enumerate(preferred, start=1):
                    vals_list.append(
                        {
                            "person_id": person.id,
                            "location_id": location.id,
                            "sequence": sequence * 10,
                        }
                    )
        self.env["fsm.location.person"].create(vals_list)

    def _phoenix_orders(self, routes, workers, locations, dates, team):
        dayroute_vals = []
        for route_index, route in enumerate(routes):
            for day in dates:
                dayroute_vals.append(
                    {
                        "name": f"{route.name} {day.isoformat()}",
                        "route_id": route.id,
                        "date": day,
                        "person_id": workers[route_index * WORKERS_PER_ROUTE].id,
                        "team_id": team.id,
                    }
                )
        self.env["fsm.order"].with_context(
            tracking_disable=True, mail_notrack=True
        ).search([]).write(
            {"scheduled_date_start": False, "dayroute_id": False}
        )
        dayroutes = self._ensure_records(
            "fsm.route.dayroute",
            [],
            "phoenix_dayroute",
            dayroute_vals,
            leftovers=True,
        )
        stage = self.env["fsm.order"]._default_stage_id()
        order_vals = []
        for route_index, route in enumerate(routes):
            route_locations = locations[
                route_index * LOCATIONS_PER_ROUTE : (route_index + 1)
                * LOCATIONS_PER_ROUTE
            ]
            lead = workers[route_index * WORKERS_PER_ROUTE]
            for date_index, day in enumerate(dates):
                dayroute = dayroutes[route_index * len(dates) + date_index]
                for stop in range(ORDERS_PER_DAYROUTE):
                    location = route_locations[
                        (stop + date_index) % len(route_locations)
                    ]
                    order_vals.append(
                        {
                            "location_id": location.id,
                            "person_id": lead.id,
                            "dayroute_id": dayroute.id,
                            "team_id": team.id,
                            "scheduled_date_start": self._phoenix_at(
                                day, STOP_HOURS[stop]
                            ),
                            "scheduled_duration": 1.0,
                            "sequence": (stop + 1) * 10,
                            "description": f"<p>{TASKS[stop]} at {location.name}.</p>",
                            "stage_id": stage.id,
                        }
                    )
        self._ensure_records(
            "fsm.order",
            [
                "fieldservice_portal.fsm_order_demo",
                "fieldservice_route.order_route_demo_1",
                "fieldservice_route.order_route_demo_2",
                "fieldservice_route.order_route_demo_3",
                "fieldservice_sign.fsm_order_sign_demo",
            ],
            "phoenix_order",
            order_vals,
            leftovers=True,
        )

    def _ensure_records(self, model, seed_xmlids, prefix, vals_list, leftovers=False):
        """Reuse demo records, then create whatever is still missing."""
        records = []
        seen = set()

        def add(record):
            if record and record.id not in seen and len(records) < len(vals_list):
                records.append(record)
                seen.add(record.id)

        for xmlid in seed_xmlids:
            add(self._xmlid_record(model, xmlid))
        for index in range(1, len(vals_list) + 1):
            add(
                self._xmlid_record(
                    model, f"fieldservice_geoengine.{prefix}_{index:02d}"
                )
            )
        if leftovers and len(records) < len(vals_list):
            extra = self.env[model].search(
                [("id", "not in", list(seen) or [0])],
                order="id",
                limit=len(vals_list) - len(records),
            )
            for record in extra:
                add(record)
        Model = self.env[model].with_context(tracking_disable=True, mail_notrack=True)
        for index, record in enumerate(records):
            record.with_context(tracking_disable=True, mail_notrack=True).write(
                vals_list[index]
            )
            self._tag_xmlid(record, f"{prefix}_{index + 1:02d}")
        while len(records) < len(vals_list):
            index = len(records)
            record = Model.create(vals_list[index])
            self._tag_xmlid(record, f"{prefix}_{index + 1:02d}")
            records.append(record)
        return Model.browse([record.id for record in records])

    def _xmlid_record(self, model, xmlid):
        module, name = xmlid.split(".", 1)
        imd = self.env["ir.model.data"].sudo().search(
            [("module", "=", module), ("name", "=", name), ("model", "=", model)],
            limit=1,
        )
        if not imd:
            return self.env[model]
        record = self.env[model].browse(imd.res_id).exists()
        if not record:
            imd.unlink()
            return self.env[model]
        return record

    def _tag_xmlid(self, record, name):
        imd = self.env["ir.model.data"].sudo()
        existing = imd.search(
            [("module", "=", "fieldservice_geoengine"), ("name", "=", name)],
            limit=1,
        )
        if existing:
            if existing.model != record._name or existing.res_id != record.id:
                existing.write(
                    {
                        "model": record._name,
                        "res_id": record.id,
                        "noupdate": True,
                    }
                )
            return
        imd.create(
            {
                "module": "fieldservice_geoengine",
                "name": name,
                "model": record._name,
                "res_id": record.id,
                "noupdate": True,
            }
        )
