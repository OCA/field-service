To use this module, you can:

1. Create `fsm.order.type` Maintenance with internal type = Repair
2. Create `fsm.template` Maintenance with type Maintenance (created on step 1)
3. Create a `fsm.recurring.template` Daily Maintenance with
   - order template = maintenance (created on step 2)
4. Create a SO with a product with creation of new equipment activated
and the generation of recurring orders.
5. Confirm and deliver → you get a new `fsm.equipment` linked to the delivered product
and a `fsm.recurring.order` linked to the SO:
6. On the `fsm.recurring.order`:
   - set the equipment to the one delivered
7. click Start

This will create one `fsm.order` per equipment and one `repair.order` by `fsm.order`.
