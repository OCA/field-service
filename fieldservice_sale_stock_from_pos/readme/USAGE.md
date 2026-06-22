# Instructions for Creating FSM Orders from Point of Sale

## 1. Create or Edit a Product

Configure the product to create an FSM order per sale and add it to the Point of Sale (POS).

## 2. Configure Stock Update Behavior

In the POS settings, you can choose how stock updates:

- **Real-time**: FSM orders and pickings will be linked immediately.
- **On session close**: FSM orders and pickings will be linked only when the POS session is closed.

## 3. Configure the user who will recive notifications on fsm order creation

In the POS settings, under Sale Order Creation you can set the person who will recive notifications to review the orders and assign them.

## 4. Open a New Point of Sale Session

## 5. Add the Configured Product to the Order

## 6. Select a Customer

## 7. Click on "Create Order"

## 8. Behavior Based on the Selected Option

### Create Draft Sale Order

- A draft Sale Order will be created.
- To process it, go to **Quotations/Orders**, select the order, and confirm it.
- **Real-time stock**: An FSM order will be created and linked immediately to the pickings.
- **Non-real-time stock**: You will need to close the POS session to link the FSM order to the pickings.

### Create Confirmed Sale Order

- A confirmed Sale Order will be created directly.
- This flow works the same whether stock updates are real-time or not.
- An FSM order will be created and linked to the Sale Order automatically.

### Create Delivered/Invoiced Sale Order

- These options will automatically complete both the FSM order and the associated pickings.
- The difference between them is that **Invoiced** will also generate an invoice.

---

# Refunds

Refunds can be processed directly from the POS. The behavior varies depending on whether it is a full or partial refund:

## Full Refunds

- If the FSM order is not yet completed, it will be canceled.

## Partial Refunds

- The picking will be updated by removing the refunded products.
