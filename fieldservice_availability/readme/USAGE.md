### 1. Defining Delivery Time Ranges
1. Navigate to **Field Service > Configuration > Availability > Delivery Time Ranges**.
2. Click **New** to create a time range.
3. Set the **Start Time** and **End Time** (e.g., `08:00` to `14:00`).
4. To create a **Default Schedule** (active year-round), leave the *Seasonal Validity* section empty.
5. To create a **Seasonal Schedule** (e.g., summer hours):
   - Select the **Start Month** and **Start Day** (e.g., June 1).
   - Select the **End Month** and **End Day** (e.g., September 30).

### 2. Assigning Schedules to Routes
1. Navigate to **Field Service > Master Data > Routes**.
2. Select a route and navigate to the **Default Delivery Schedule** section.
3. Select one or more **Delivery Time Ranges** (allowing 1 default year-round schedule and optional seasonal schedules).

### 3. Assigning Schedules to Locations
1. Navigate to **Field Service > Master Data > Locations**.
2. Select a location and select specific **Delivery Time Ranges** for this location. Any schedule assigned directly to the location will override route-level defaults.

### 4. Configuring Blackout and Stress Days
1. Navigate to **Field Service > Configuration > Availability**.
2. Select **Blackout Days**, **Blackout Groups**, or **Stress Days** to add operational exceptions or demand surges.