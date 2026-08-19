- Navigate to Field Service.

- Create or edit a Field Service Order.

- In the Kanban view, the scheduled time range is automatically computed
  based on the **Scheduled Start (ETA)** and **Scheduled End** fields.
  The customer address and contact details (partner's phone and mobile)
  are also displayed on the order card, if set.

- To configure the format of the scheduled time range, go to
  **Configuration \> Settings \> Technical \> Orders \> Schedule Time
  Range Format** to choose between **time range only format** (e.g.
  15:30 - 17:30) or **date and time range format**.

- Regarding the date and time range format, if the schedule_date_start
  and schedule_date_end fields fall on the same date, the date is
  displayed only once (e.g. 19/02/2025 15:30 - 17:30). If the dates
  differ, both the start and end dates are displayed (e.g. 19/02/2025
  15:30 - 20/02/2025 17:30).

- The date and time format respects the user's language settings and
  their associated date and time format.

  - For example, if the user's language date format is set to `%m/%d/%Y`
    (e.g. **02/19/2025**) with a time format of `%I:%M %p` (e.g. **3:30
    PM**), the scheduled time range will be displayed as **02/19/2025
    3:30 PM - 02/19/2025 5:30 PM**.

  -If the user's language date format is set to `%d/%m/%Y` (e.g.
  **19/02/2025**) and a time format of `%H:%M:%S` (e.g. **15:30:00**),
  the scheduled time range will be displayed as **19/02/2025 15:30 -
  19/02/2025 17:30**.
