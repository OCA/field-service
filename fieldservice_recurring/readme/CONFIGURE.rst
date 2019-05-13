To configure this module, you need to:

* Setup your Frequencies to establish recurring rules

1. In fieldservice app go to Menu > Configuration > Orders > Frequencies
2. Create a Frequency
3. Setup your Frequency by giving it a descriptive name, set your interval
   and the interval type. Use the additional settings to build a recurring rule
   based on python's dateutil rrule parameters.


* Setup your Frequency Rule Sets used to calculate recurring order dates

1. In fieldservice app go to Menu > Configuration > Orders > Frequency Rule Set
2. Create a Frequency Rule Set
3. Setup your Frequency Rule by first giving it a descriptive name. Complete
   the form by entering the number of days ahead this rule will schedule work.
4. Finally, choose which Frequencies this rule will use to compute the dates
   used for scheduling.


* Setup your recurring order templates to define standard recurring orders

1. In fieldservice app go to Menu > Configuration > Orders > Recurring Templates
2. Name the template and set fields to define which order template is repeated
   and what Frequency Rule Set will be used
