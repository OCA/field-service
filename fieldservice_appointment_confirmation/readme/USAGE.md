The **Request Confirmation** button only appears on a field service order that
has an assigned worker, a scheduled date, a customer email, and is in a stage
where **Allow Appointment Confirmation Request** is ticked (see *Configuration*):

1. Press **Request Confirmation**. A mail composer opens with the pre-filled
   request template; edit it if needed and send it. The appointment status
   becomes *Requested* and the customer receives the email.

   ![Request Confirmation button on the order](../static/img/readme/01_request_button.png)

   ![Pre-filled mail composer](../static/img/readme/02_request_wizard.png)

   ![Confirmation request email](../static/img/readme/13_email_request.png)

2. From the email (secure link, no login) the customer can:

   - **Confirm Appointment**: the status becomes *Confirmed*, a note is logged,
     the followers and the assigned worker are notified and the customer is
     offered an `.ics` download.

     ![Customer confirmation page](../static/img/readme/09_portal_confirm.png)

     ![Confirmation success with the .ics download](../static/img/readme/11_portal_confirmed.png)

   - **Reschedule**: the customer picks an available slot of the assigned
     worker; the order date is updated and the appointment is **automatically
     confirmed** on the new date (shown as *Confirmed (rescheduled)*). The
     customer receives a confirmation email and can download the `.ics`.

     ![Reschedule page with the worker available slots](../static/img/readme/10_portal_reschedule.png)

     ![Confirmed (rescheduled) badge on the order](../static/img/readme/04_confirmed_rescheduled.png)

3. If the appointment date has already passed, the confirmation link redirects
   the customer to the reschedule page to pick a new future slot. An invalid or
   expired token shows a friendly page instead:

   ![Invalid or expired link](../static/img/readme/12_portal_invalid.png)

Confirmed appointments are highlighted on the order form with a ribbon, and can
be filtered or grouped by appointment status from the list view:

![Confirmed ribbon on the order form](../static/img/readme/03_confirmed_ribbon.png)

![Filters and group by appointment status](../static/img/readme/06_filters_groupby.png)
