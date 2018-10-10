v1.3.8
======
* Fix help group page using old field

v1.3.7
======
* Add customer close button
* Limit help pages to 5 per help group with a more link
* Administrator now defaults to Support Manager to help reduce install confusion

v1.3.6
======
* User accounts created through the create account link are now added to the portal group instead of the public group to resolve login issues

v1.3.5
======
* Fix business hours field missing resource module dependacy

v1.3.4
======
* Ability to limit which user groups can select a category

v1.3.3
======
* Add close date to customer website portal

v1.3.2
======
* Assigned user filter for internal users (employees) only

v1.3.1
======
* Remove dependency on CRM module

v1.3.0
======
* (BACK COMPATABLITY BREAK) Remove old Sales Manager permissions
* Group and permission overhaul (Support Client, Support Staff, Support Manager)
* Update documentation to reflect menu changes and permission overhaul

v1.2.14
=======
* Adding sequence for ticket number, deleting ticket number display
* Migrate fake ticket number system to sequence system
* Spanish tranlation
* Timezone in website view
* Various view improvements

v1.2.13
=======
* Optional priority field on website

v1.2.12
=======
* Website filter state for tickets
* Hide SLA resume and pause buttons if no SLA is assigned to the ticket
* Choose which states get classified as unattended

v1.2.11
=======
* Unlinked page to list help pages by support group

v1.2.10
=======
* Fix SLA business hours timer and add support for holidays via the hr_public_holidays module

v1.2.9
======
* Permission for SLA Alerts

v1.2.8
======
* SLA alert emails

v1.2.7
======
* reCAPTCHA implementation since the honey pot is not bullet proof

v1.2.6
======
* SLA tickets now have a timer that counts down, you can select between always count and business hours only + plus/resume timer

v1.2.5
======
* Ability to assign SLA to contact and ultimately to their tickets

v1.2.4
======
* Information only SLA

v1.2.3
======
* Planned date now in default wrapper email template, formatted and localised
* Default wrapper email template now uses fake/display ticket_number not id

v1.2.2
======
* Portal access key is generated when ticket is manually created or through email / website

v1.2.1
======
* Permission fix for approval system

v1.2.0
======
* Ability to tag support tickets

v1.1.1
======
* Support ticket now defaultly searches by subject rather then partner...

v1.1.0
======
* Port approval system over from version 10
* Add approvals to portal
* Email notifacation on approval / rejection
* Default approval compose email is now a email tempalte rather then hard coded.

v1.0.12
=======
* Changing subcategory now automatically adds th extra fields

v1.0.11
=======
* Extra field type and label is required

v1.0.10
=======
* Show extra fields incase someone wants to manuall add the data
* Add new channel field which tracks the source of the ticket (website / email)

v1.0.9
======
* Remove kanban "+" and create since it isn't really compatable

v1.0.8
======
* Fix subcategory change not disappearing
* States no longer readonly
* Move Kanban view over from Odoo 10

v1.0.7
======
* Fix subcategories

v1.0.6
======
* Fix multiple ticket delete issue

v1.0.5
======
* Change default email wrapper to user

v1.0.4
======
* Remove obsolete support@ reply wrapper

v1.0.3
======
* Fix website ticket attachment issue

v1.0.2
======
* Fix settings screen and move menu

v1.0.1
======
* Forward fix custom field mismatch

v1.0
====
* Port to version 11