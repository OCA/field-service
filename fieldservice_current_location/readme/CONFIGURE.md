To comply with [Nominatim’s usage policy](https://operations.osmfoundation.org/policies/nominatim/), each instance must have a unique **User-Agent** string configured.  
This value is stored in the system parameter:
`nominatim.user_agent`

If not set manually, it will be automatically generated the first time the geolocation feature is used  
and stored under **Settings → Technical → System Parameters**.

> You can optionally define a custom value (for example, including your company name or contact email)  
> to make API requests more easily identifiable and compliant with OpenStreetMap policies.
