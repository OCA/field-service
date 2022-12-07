import logging
import odoo.http as http

_logger = logging.getLogger(__name__)

class FieldserviceEquipmentWebsiteController(http.Controller):

    @http.route('/equipment/<serial>/',type="http", auth='user', website=True)
    def get_equipment(self, serial):
        # Validate format of path param (serial)
        # Get equipment for the serial number (if not, raise error)
        Equipment = http.request.env['fsm.equipment']
        # equipment = Equipment.search([['id','=',1]])
        equipment = {
            "id": serial,
            "name": f"equipment: {serial}"

        }
        _logger.info("Controller testing...")
        # Render template with equiment data
        return http.request.render('fieldservice_equipment_website.index', {
            'equipment': equipment,
        })