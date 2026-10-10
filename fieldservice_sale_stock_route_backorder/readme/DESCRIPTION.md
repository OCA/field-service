This module introduces a new wizard in the FSM order form view to adjust
deliveries. This wizard allows setting the quantity to deliver for each
outgoing product, and it also supports adding new products that were not
part of the initial demand.

By default, the system checks the **reserved quantity** on each stock
move and considers the **free stock available** in the warehouse for
each **storable product**. If additional stock is available beyond the
reserved quantity and has not been reserved by another stock move, it
allows delivering more than the initially ordered amount, providing
flexibility when extra stock is on hand. However, it still ensures that
deliveries do not exceed the actual stock available in the warehouse. On
the other hand, **Consumable products** can always be over-delivered, as
they do not have stock constraints.

Example Scenario 1. An order requests **70 units** of a product. 2.
Initially, only **40 units** are available and reserved, so the system
prevents delivering more than 40. 3. Later, additional stock arrives,
increasing available inventory to **100 units**. 4. If no other stock
moves have reserved the extra **30 units**, the system allows delivering
**up to 100 units**, even though the initial demand was 70. 5.
Additionally, new products can be added to the delivery through the
wizard, and stock moves will be created for these new products, ensuring
that quantities are validated and processed as part of the overall
delivery.

Once confirmed, the system validates the picking and creates a backorder
sale if any of the initially requested quantities cannot be delivered
and the product has the 'create backorder sale' option enabled. This
backorder sale will include the remaining quantities that could not be
delivered and will be scheduled for the next available route day,
allowing for future processing and fulfillment.

When all quantities have been delivered, the FSM order is marked as
completed automatically.
