# Copyright 2026 Antoni Marroig (APSL-Nagarro) <antoni.marroig@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestFSMRouteDayRouteSummary(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.stage_cancelled = cls.env.ref("fieldservice.fsm_stage_cancelled")
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        Product = cls.env["product.product"]
        cls.product_water = Product.create(
            {"name": "Water Bottle", "is_storable": True, "weight": 2.0}
        )
        cls.product_cup = Product.create(
            {"name": "Paper Cup", "is_storable": True, "weight": 0.5}
        )
        Quant = cls.env["stock.quant"]
        Quant._update_available_quantity(cls.product_water, cls.stock_location, 20)
        Quant._update_available_quantity(cls.product_cup, cls.stock_location, 5)
        cls.customer = cls.env["res.partner"].create({"name": "Customer"})
        Location = cls.env["fsm.location"]
        # With coordinates, fieldservice_geoengine does not geolocalize the
        # locations through an external service
        geo_vals = (
            {"partner_latitude": 39.57, "partner_longitude": 2.65}
            if "partner_latitude" in Location._fields
            else {}
        )
        cls.location_1 = Location.create(
            {
                "name": "Office <Main>",
                "owner_id": cls.customer.id,
                "street": "Main Street 1",
                "city": "Palma",
                "zip": "07001",
                "phone": "+34 971 000 000",
                "notes": "<p>Ring the bell twice</p>",
                **geo_vals,
            }
        )
        cls.location_2 = Location.create(
            {
                "name": "Warehouse",
                "owner_id": cls.customer.id,
                "street": "Harbour Road 2",
                "city": "Inca",
                **geo_vals,
            }
        )
        cls.person = cls.env["fsm.person"].create({"name": "Driver"})
        cls.dayroute = cls._create_dayroute()
        # Order 1: deliveries, one of them with only 5 of 12 units in stock,
        # and a pick-up
        cls.order_1 = cls._create_fsm_order(cls.location_1, 20)
        cls.delivery_1 = cls._create_picking(
            cls.order_1,
            "outgoing",
            [(cls.product_water, 3, cls.uom_unit), (cls.product_cup, 12, cls.uom_unit)],
        )
        cls.pickup_1 = cls._create_picking(
            cls.order_1, "incoming", [(cls.product_water, 2, cls.uom_unit)]
        )
        # Order 2: a delivery fully reserved
        cls.order_2 = cls._create_fsm_order(cls.location_2, 10)
        cls.delivery_2 = cls._create_picking(
            cls.order_2, "outgoing", [(cls.product_water, 5, cls.uom_unit)]
        )

    @classmethod
    def _create_dayroute(cls):
        return cls.env["fsm.route.dayroute"].create(
            {"person_id": cls.person.id, "date": fields.Date.today()}
        )

    @classmethod
    def _create_fsm_order(cls, location, sequence, dayroute=None, **vals):
        return cls.env["fsm.order"].create(
            {
                "location_id": location.id,
                "dayroute_id": (dayroute or cls.dayroute).id,
                "sequence": sequence,
                **vals,
            }
        )

    @classmethod
    def _create_picking(cls, order, code, lines):
        """Create and reserve a delivery (outgoing) or a pick-up (incoming)
        linked to the order through its procurement group, as
        fieldservice_sale_stock does on sale orders."""
        if code == "outgoing":
            picking_type = cls.warehouse.out_type_id
            source, destination = cls.stock_location, cls.customer_location
        else:
            picking_type = cls.warehouse.in_type_id
            source, destination = cls.customer_location, cls.stock_location
        group = cls.env["procurement.group"].create(
            {"name": order.name, "fsm_order_id": order.id}
        )
        picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": picking_type.id,
                "group_id": group.id,
                "partner_id": cls.customer.id,
                "location_id": source.id,
                "location_dest_id": destination.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "product_uom": uom.id,
                            "location_id": source.id,
                            "location_dest_id": destination.id,
                            "group_id": group.id,
                            "fsm_order_id": order.id,
                        }
                    )
                    for product, qty, uom in lines
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        return picking

    def _get_summary(self, dayroute=None):
        dayroute = dayroute or self.dayroute
        # Rows come from an SQL query: drop the values cached by previous reads
        self.env.invalidate_all()
        return {
            line.product_id: (line.quantity, line.reserved_quantity, line.weight)
            for line in dayroute.summary_line_ids
        }

    def _get_html(self, dayroute=None):
        return str((dayroute or self.dayroute).location_breakdown_html)

    def test_product_totals(self):
        summary = self._get_summary()
        # Pick-ups are not loaded
        self.assertEqual(
            summary,
            {
                self.product_water: (8.0, 8.0, 16.0),
                self.product_cup: (12.0, 5.0, 6.0),
            },
        )
        self.assertEqual(
            self.dayroute.summary_line_ids.uom_id, self.product_water.uom_id
        )
        self.assertAlmostEqual(self.dayroute.total_weight, 22.0)
        self.assertEqual(
            self.dayroute.weight_uom_name,
            self.env[
                "product.template"
            ]._get_weight_uom_name_from_ir_config_parameter(),
        )

    def test_open_orders_keeps_deliveries(self):
        """Opening an order recomputes its transfer counters, which rewrites
        its moves from its transfers (fieldservice_stock): the load sheet must
        not change."""
        (self.order_1 | self.order_2)._compute_picking_ids()
        self.assertEqual(self._get_summary()[self.product_water][0], 8.0)
        self.assertIn(self.product_cup.display_name, self._get_html())

    def test_product_totals_match_python_totals(self):
        python_totals = self.dayroute._get_load_sheet_totals()
        summary = self._get_summary()
        self.assertEqual(set(python_totals), set(summary))
        for product, quantity in python_totals.items():
            self.assertAlmostEqual(summary[product][0], quantity)

    def test_product_totals_unit_conversion(self):
        dayroute = self._create_dayroute()
        order = self._create_fsm_order(self.location_2, 10, dayroute)
        self._create_picking(order, "outgoing", [(self.product_cup, 1, self.uom_dozen)])
        # All the cups in stock are already reserved by the other day route
        self.assertEqual(
            self._get_summary(dayroute), {self.product_cup: (12.0, 0.0, 6.0)}
        )

    def test_totals_follow_order_changes(self):
        # Remove an order from the day route
        self.order_2.dayroute_id = False
        self.assertEqual(self._get_summary()[self.product_water][0], 3.0)
        self.assertAlmostEqual(self.dayroute.total_weight, 12.0)
        # Add it back and deliver it: it is not to load anymore
        self.order_2.dayroute_id = self.dayroute
        self.assertEqual(self._get_summary()[self.product_water][0], 8.0)
        self.delivery_2.move_ids.picked = True
        self.delivery_2._action_done()
        self.assertEqual(self._get_summary()[self.product_water][0], 3.0)
        # Add a new order
        order = self._create_fsm_order(self.location_2, 30)
        self._create_picking(order, "outgoing", [(self.product_cup, 4, self.uom_unit)])
        self.assertEqual(self._get_summary()[self.product_cup][:2], (16.0, 5.0))
        # Cancel a delivery
        self.delivery_1.action_cancel()
        self.assertEqual(self._get_summary(), {self.product_cup: (4.0, 0.0, 2.0)})

    def test_cancelled_orders_are_excluded(self):
        self.order_1.stage_id = self.stage_cancelled
        self.assertEqual(self._get_summary(), {self.product_water: (5.0, 5.0, 10.0)})
        self.assertAlmostEqual(self.dayroute.total_weight, 10.0)
        self.assertNotIn(self.order_1.name, self._get_html())
        self.delivery_2.action_cancel()
        self.assertFalse(self._get_summary())
        self.assertIn("No products to deliver or pick up.", self._get_html())

    def test_breakdown_cards(self):
        html = self._get_html()
        # Cards follow the order sequence of the route
        self.assertLess(html.index(self.order_2.name), html.index(self.order_1.name))
        self.assertIn("#1 -", html)
        self.assertIn("#2 -", html)
        # Location data is escaped
        self.assertIn("Office &lt;Main&gt;", html)
        self.assertNotIn("Office <Main>", html)
        self.assertIn("Main Street 1", html)
        self.assertIn('href="tel:+34 971 000 000"', html)
        self.assertIn(f"/fsm.order/{self.order_1.id}", html)
        self.assertIn(self.product_water.display_name, html)
        self.assertIn(self.product_cup.display_name, html)
        # Red badge for the cups with missing stock, yellow one for the pick-up
        self.assertEqual(html.count("text-bg-danger"), 1)
        self.assertEqual(html.count("text-bg-warning"), 1)
        self.assertIn("fa-undo", html)
        self.assertIn("Pick up", html)
        self.assertNotIn("Completed", html)
        stops = self.dayroute._get_load_sheet_stops()
        self.assertEqual(
            [stop["order"] for stop in stops], [self.order_2, self.order_1]
        )
        # Deliveries first, then pick-ups
        self.assertEqual(
            [
                (
                    line["product"],
                    line["quantity"],
                    line["is_pickup"],
                    line["is_missing_stock"],
                )
                for line in stops[1]["lines"]
            ],
            [
                (self.product_water, 3.0, False, False),
                (self.product_cup, 12.0, False, True),
                (self.product_water, 2.0, True, False),
            ],
        )

    def test_breakdown_follows_order_changes(self):
        self.order_1.sequence = 1
        html = self._get_html()
        self.assertLess(html.index(self.order_1.name), html.index(self.order_2.name))
        self.order_2.dayroute_id = False
        self.assertNotIn(self.order_2.name, self._get_html())
        # Delivered products are not displayed anymore
        self.delivery_1.move_ids.picked = True
        self.delivery_1.with_context(cancel_backorder=True)._action_done()
        html = self._get_html()
        self.assertNotIn(self.product_cup.display_name, html)
        self.assertIn("Pick up", html)

    def test_completed_order(self):
        """Completed orders are displayed in green with what was delivered."""
        self.delivery_2.move_ids.picked = True
        self.delivery_2._action_done()
        self.order_2.action_complete()
        html = self._get_html()
        self.assertEqual(html.count("border-success"), 1)
        self.assertIn("Completed", html)
        stops = self.dayroute._get_load_sheet_stops()
        self.assertTrue(stops[0]["is_completed"])
        self.assertFalse(stops[1]["is_completed"])
        self.assertEqual(
            [(line["product"], line["quantity"]) for line in stops[0]["lines"]],
            [(self.product_water, 5.0)],
        )
        self.assertFalse(stops[0]["lines"][0]["is_missing_stock"])
        # Delivered products are not to load anymore
        self.assertEqual(self._get_summary()[self.product_water][0], 3.0)
        self.assertEqual(
            self.dayroute._get_load_sheet_totals()[self.product_water], 3.0
        )

    def test_weight_label_with_unit(self):
        weight_uom_name = self.env[
            "product.template"
        ]._get_weight_uom_name_from_ir_config_parameter()
        fields = self.env["fsm.route.dayroute.product.summary"].fields_get(
            ["weight"], ["string"]
        )
        self.assertEqual(fields["weight"]["string"], f"Weight ({weight_uom_name})")

    def test_weight_uom_name(self):
        """The weight unit follows the product weight setting."""
        summary_lines = self.dayroute.summary_line_ids
        self.assertEqual(self.dayroute.weight_uom_name, "kg")
        self.assertEqual(set(summary_lines.mapped("weight_uom_name")), {"kg"})
        self.env["ir.config_parameter"].sudo().set_param("product.weight_in_lbs", "1")
        self.env.invalidate_all()
        self.assertEqual(self.dayroute.weight_uom_name, "lb")
        self.assertEqual(set(summary_lines.mapped("weight_uom_name")), {"lb"})
        fields = summary_lines.fields_get(["weight"], ["string"])
        self.assertEqual(fields["weight"]["string"], "Weight (lb)")

    def test_breakdown_notes(self):
        # Without order notes, the location notes are displayed
        self.order_1.description = "<p><br></p>"
        self.assertIn("Ring the bell twice", self._get_html())
        # The order notes have priority over the location ones
        self.order_1.description = "<p>Leave it at the reception</p>"
        html = self._get_html()
        self.assertIn("Leave it at the reception", html)
        self.assertNotIn("Ring the bell twice", html)

    def test_empty_dayroute(self):
        dayroute = self._create_dayroute()
        self.assertFalse(dayroute.summary_line_ids)
        self.assertEqual(dayroute.total_weight, 0.0)
        self.assertIn(
            "There are no orders to deliver in this day route.",
            self._get_html(dayroute),
        )

    def test_pickup_only_order(self):
        """An order with only pick-ups (e.g. a sale order with only negative
        lines) is displayed with them, but nothing is loaded for it."""
        dayroute = self._create_dayroute()
        order = self._create_fsm_order(self.location_2, 10, dayroute)
        self._create_picking(order, "incoming", [(self.product_cup, 3, self.uom_unit)])
        self.assertFalse(self._get_summary(dayroute))
        self.assertEqual(dayroute.total_weight, 0.0)
        lines = dayroute._get_load_sheet_stops()[0]["lines"]
        self.assertEqual(
            [(line["product"], line["quantity"], line["is_pickup"]) for line in lines],
            [(self.product_cup, 3.0, True)],
        )
        html = self._get_html(dayroute)
        self.assertIn("Pick up", html)
        self.assertNotIn("No products to deliver or pick up.", html)

    def test_pickup_in_delivery_transfer(self):
        """A pick-up is never loaded, even in a transfer of a delivery
        operation type (e.g. without return operation type configured)."""
        dayroute = self._create_dayroute()
        order = self._create_fsm_order(self.location_2, 10, dayroute)
        delivery = self._create_picking(
            order, "outgoing", [(self.product_water, 2, self.uom_unit)]
        )
        self.env["stock.move"].create(
            {
                "name": self.product_cup.name,
                "picking_id": delivery.id,
                "product_id": self.product_cup.id,
                "product_uom_qty": 4,
                "product_uom": self.uom_unit.id,
                "location_id": self.customer_location.id,
                "location_dest_id": self.stock_location.id,
                "fsm_order_id": order.id,
            }
        )._action_confirm()
        self.assertEqual(
            self._get_summary(dayroute), {self.product_water: (2.0, 2.0, 4.0)}
        )
        lines = dayroute._get_load_sheet_stops()[0]["lines"]
        self.assertEqual(
            [(line["product"], line["is_pickup"]) for line in lines],
            [(self.product_water, False), (self.product_cup, True)],
        )

    def test_sale_order_flow(self):
        """Deliveries and pick-ups (negative lines) generated by a sale order
        are linked to its field service order by fieldservice_sale_stock; only
        the deliveries are loaded."""
        dayroute = self._create_dayroute()
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.customer.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product_water.id, "product_uom_qty": 3}
                    ),
                    Command.create(
                        {"product_id": self.product_cup.id, "product_uom_qty": -2}
                    ),
                ],
            }
        )
        order = self._create_fsm_order(self.location_2, 10, dayroute, sale_id=sale.id)
        sale.action_confirm()
        self.assertEqual(
            self._get_summary(dayroute), {self.product_water: (3.0, 3.0, 6.0)}
        )
        # The negative line generated a pick-up linked to the order
        pickup = order.move_ids.filtered(
            lambda move: move.product_id == self.product_cup
        )
        self.assertEqual(pickup.location_id, self.customer_location)
        lines = dayroute._get_load_sheet_stops()[0]["lines"]
        self.assertEqual(
            [(line["product"], line["quantity"], line["is_pickup"]) for line in lines],
            [(self.product_water, 3.0, False), (self.product_cup, 2.0, True)],
        )

    def test_report(self):
        html, _report_type = self.env["ir.actions.report"]._render_qweb_html(
            "fieldservice_route_dayroute_summary.action_report_dayroute_load_sheet",
            self.dayroute.ids,
        )
        html = html.decode()
        self.assertIn(self.dayroute.name, html)
        self.assertIn("Product Totals", html)
        self.assertIn("Delivery Breakdown", html)
        # The cups to load have missing stock
        self.assertEqual(html.count("text-danger fw-bold"), 2)
        self.assertIn(self.product_water.display_name, html)
        self.assertIn(self.order_1.name, html)
        self.assertIn(self.order_2.name, html)
        self.assertIn("Office &lt;Main&gt;", html)
        self.assertIn("22.00", html)

    def test_report_same_transaction(self):
        """The report is right when printed in the transaction that filled the
        day route, while its totals were cached as empty at its creation."""
        dayroute = self._create_dayroute()
        self.assertFalse(dayroute.summary_line_ids)
        order = self._create_fsm_order(self.location_2, 10, dayroute)
        self._create_picking(order, "outgoing", [(self.product_cup, 7, self.uom_unit)])
        summary_lines = dayroute._get_load_sheet_summary_lines()
        self.assertEqual(summary_lines.product_id, self.product_cup)
        self.assertEqual(summary_lines.quantity, 7.0)
        html = (
            self.env["ir.actions.report"]
            ._render_qweb_html(
                "fieldservice_route_dayroute_summary.action_report_dayroute_load_sheet",
                dayroute.ids,
            )[0]
            .decode()
        )
        self.assertNotIn("There are no products to load.", html)
        self.assertIn("3.50", html)
