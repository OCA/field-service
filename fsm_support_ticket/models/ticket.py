from odoo import api, fields, models


class SupportTicket(models.Model):
    _name = 'fsm.support.ticket'
    _description = 'Field service support tickets'
    _rec_name = 'ticket_subject'
    _translate = True

    ticket_subject = fields.Char(
        string="Subject"
    )
    ticket_categ = fields.Many2one(
        'fsm.ticket.category',
        string="Ticket Category"
    )
    customer_id = fields.Many2one('res.partner',
                                  string="Customer"
                                  )
    person_id = fields.Many2one('fsm.person',
                                string="Assigned Person"
                                )
    customer_name = fields.Char(string='Person Name')
    email = fields.Char(string="Email")
    ticket_date = fields.Date(string="Ticket Date",
                              default=fields.Date.today()
                              )
    description = fields.Text(string="Description")
    state = fields.Selection([('draft', 'Draft'),
                              ('sent_to_employee', 'Sent to Employee'),
                              ('processing', 'Processing'),
                              ('finished', 'Finished'),
                              ('cancelled', 'Cancelled')
                              ], string="State",
                             default='draft')

    @api.onchange('customer_id')
    def onchange_person(self):
        if self.customer_id:
            self.customer_name = self.customer_id.name
            self.email = self.customer_id.email
