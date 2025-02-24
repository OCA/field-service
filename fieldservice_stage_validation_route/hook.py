from odoo import SUPERUSER_ID, api
from odoo.tools.safe_eval import safe_eval

MODEL_XMLID = "fieldservice_route.model_fsm_route"
MODEL_RULE_XMLID = "fieldservice_stage_validation.fieldservice_stage_validation_models"
FIELDS_RULE_XMLID = "fieldservice_stage_validation.fieldservice_stage_validation_fields"


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for rule in [MODEL_RULE_XMLID, FIELDS_RULE_XMLID]:
        rule_to_update = env.ref(rule)
        domain = safe_eval(rule_to_update.domain_force)
        domain_section = domain[0][2]
        field = env.ref(MODEL_XMLID)
        if field.id not in domain_section:
            domain_section.append(field.id)
            domain[0] = (domain[0][0], domain[0][1], domain_section)
            rule_to_update.write({"domain_force": str(domain)})


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for rule in [MODEL_RULE_XMLID, FIELDS_RULE_XMLID]:
        rule_to_update = env.ref(rule)
        domain = safe_eval(rule_to_update.domain_force)
        domain_section = domain[0][2]
        field = env.ref(MODEL_XMLID)
        if field.id in domain_section:
            domain_section = [el for el in domain_section if el != field.id]
            domain[0] = (domain[0][0], domain[0][1], domain_section)
            rule_to_update.write({"domain_force": str(domain)})
