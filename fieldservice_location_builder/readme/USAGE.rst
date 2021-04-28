* Go to Field Service > Master Data > Locations
* Select or create a location
* In the Action menu, run the Sub-Locations Builder
* Add 4 levels with:

  * Level 1: Building, - , 1, 2
  * Level 2: Floor, - , 1, 2
  * Level 3: Unit, - , 1, 2
  * Level 4: Room, - , 1, 2

* Running the wizard should result in the following sub-locations structure:

.. code-block::

    Building - 1
        * Floor - 1
            * Unit - 1
                * Room - 1
                * Room - 2
            * Unit - 2
                * Room - 1
                * Room - 2
        * Floor - 2
            * Unit - 1
                * Room - 1
                * Room - 2
            * Unit - 2
                * Room - 1
                * Room - 2
    Building - 2
        * Floor -  1
            * Unit - 1
                * Room - 1
                * Room - 2
            * Unit - 2
                * Room - 1
                * Room - 2
        * Floor - 2
            * Unit - 1
                * Room - 1
                * Room - 2
            * Unit - 2
                * Room - 1
                * Room - 2
