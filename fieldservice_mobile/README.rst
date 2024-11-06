.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

====================
Field Service Mobile
====================

This module is manage FSM mobile stages based on configuration.

Configuration
=============

To configure this module, you need to:

* Go to Field Service > Configuration > Stages.
* Check Display in Mobile for display stage in FSM Mobile.
* Check Display in Odoo for display stage in Odoo FSM Order.
* Select a server action based on Stages.

* Manage domain on Automated Actions based on Stage sequence.

For Example:- If the Started stage sequence is 6.

* Go to Settings > Automated Actions > FSM Order Started Stage Update > Apply on > [["stage_id.sequence","=",6]]

Features on the mobile application will be visible depending on the groups set on this model. 

Usage
=============
1) Navigate to the "Field Service" application
2) Under menu item "Configuration", select "FSM Mobile Features"
3) Select Installed Modules for FSM Mobile Dynamic Menu and it's records
4) Select a feature and add/remove groups

Credits
=======

* Open Source Integrators <https://opensourceintegrators.com>
* Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>

Contributors
~~~~~~~~~~~~

* Wolfgang Hall <whall@opensourceintegrators.com>
* Sandip Mangukiya <smangukiya@opensourceintegrators.com>
* Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>
* Ammar Officewala <aofficewala@opensourceintegrators.com>
