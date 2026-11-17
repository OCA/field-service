This module adds configurable customer signing features on Field Service orders:

* **On-site signature capture** — uses the native signature widget and the
  signature fields already provided by `fieldservice` (`signature`,
  `signed_by`, `signed_on`). Capture can be enabled or disabled per company,
  and optionally required before an order can be completed.
* **Document signing** — integrates with `sign_oca` to launch a signature
  request for a document linked to the order, expose its status on the order,
  and optionally require a signed document before completion.

Both features are independent. An administrator can enable none, either one,
or both from Field Service settings.
