To configure this module, you need to:

- Go to Field Service \> Configuration \> Settings

You need to add attribute mention below with the tag \<timeline\> as
base element.

- colors (optional): it allows to set certain specific colors if the
  expressed condition (JS syntax) is met.
- custom_color (optional): it allows to set custom color for fsm.stages
  example custom_color = "true". And there is minor condition to follow
  to implement this as. Define any one stage color condition like
  colors="#ffffff:stage_id=='New';"
