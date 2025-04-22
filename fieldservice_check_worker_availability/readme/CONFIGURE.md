To configure this module, you need to:

- Create a FSM Person 
- Configure its Working Schedule: Go to Field Service -> Master Data -> Workers -> Select the worker and stablish the field
- To configure a worker's leave, go to the Working Schedule form and click the Time Off smart button.
- Now create a new record for this resource
- Create a new FSM Order and assign it to the configured worker
- Select a Scheduled Start 
- If the scheduled start falls within a worker's leave or non-working period, an error will be raised.