import logging
import odoo.http as http

_logger = logging.getLogger(__name__)

class FieldserviceEquipmentWebsiteController(http.Controller):

    @http.route('/equipment/<serial>/',type="http", auth='user', website=True)
    def get_equipment(self, serial):

        Lots = http.request.env['stock.production.lot']
        lot_obj = Lots.search([['name','ilike',serial]], limit=1)

        return http.request.render('fieldservice_equipment_website.index', {
            "lot_obj": lot_obj
        })