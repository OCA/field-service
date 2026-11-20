1. Grant a customer contact portal access (Settings > Users, "Grant portal
   access").
2. As that portal user, open **My Account**: an **Equipments** card lists the
   equipments whose owner or manager belongs to the user's company, plus any
   equipment the user follows.
3. Internal users can share a direct link with a token from the equipment
   form ("Share" behavior provided by `portal.mixin`). Without a valid token,
   the detail page is only shown to users allowed to read the equipment; a
   bare `/my/equipments/<id>` link never exposes it to anonymous visitors.
