From the equipments page of the portal, a user can *Register a Location*
(`/my/locations/new`), created under the company of the user, and *Register an
Equipment* (`/my/equipments/new`) at one of those locations, from a trackable
product and a typed serial number; the lot is found or created under the
selected product.

Override `_get_registrable_products_domain()` to narrow the products offered.
