From the equipments page of the portal, a user can *Register a Location*
(`/my/locations/new`), owned by the commercial partner of the user and
attached to its root location, and *Register an Equipment*
(`/my/equipments/new`) at one of those locations, from a trackable product and
a typed serial number. The product list shows the first matches of its search
box. The lot is found or created under the selected product, in the company of
the equipment. A serial number already linked to another equipment, or an
equipment name already in use, is reported on the form.

Override `_get_registrable_products_domain()` to narrow the products offered.
