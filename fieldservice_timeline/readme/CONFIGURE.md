The Field Service Web Timeline View module can be used with minimal
initial configuration.

## Order Stages

The stage of an order is used to monitor its progress. Stages can be
configured based on your company's specific business needs. A basic set
of order stages comes pre-configured for use.

1.  Go to *Field Service \> Configuration \> Stages*
2.  Create or edit a stage
3.  Set the name for the stage.
4.  Set the sequence order for the stage.
5.  Select *Order* type to apply this stage to your orders.
6.  Additonally, you can set a color for the stage.

You need to add attribute mention below with the tag \<timeline\> as
base element.

- colors (optional): it allows to set certain specific colors if the
  expressed condition (JS syntax) is met.
- custom_color (optional): it allows to set custom color for fsm.stages
  example custom_color = "true". And there is minor condition to follow
  to implement this as. Define any one stage color condition like
  colors="#ffffff:stage_id=='New';"
