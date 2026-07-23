Navigate to Field Service \> Configuration \> Availability. Once there,
you can select Delivery Time Ranges, Blackout Days, Blackout Groups or Stress Days to
create new records.

Steps to restrict blackout days for Scheduled Start (ETA) orders with the same date

1. Set up Blackout Days on Configuration > Blackout Groups and create or edit one with blackout days
2. Go to Field Service > Master Data > Routes > Create or edit route and assign Blackout Group Days and a Person
3. Create a Field Service order and set up Scheduled Start (ETA) with date that you put on blackout days and the Odoo will throw an error
