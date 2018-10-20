import logging

from odoo import api, exceptions, fields, models, _

_logger = logging.getLogger(__name__)


class PartnerOperation(models.Model):
    _inherit = 'res.partner'

    mail_compose_wiz = fields.Many2one('fsm.compose.mail',
                                       string="Mail compose wizard"
                                       )


class EmployeeOperation(models.Model):
    _inherit = 'fsm.person'

    mail_compose_wiz = fields.Many2one('fsm.compose.mail',
                                       string="Mail compose wizard"
                                       )


# This model is used to create a wizard for composing mails to
# customers and employees
class MailNotification(models.Model):
    _name = 'fsm.compose.mail'

    email_from = fields.Char(string="From")
    recipient = fields.One2many('res.partner',
                                'mail_compose_wiz',
                                string="Recipients"
                                )
    recipient_person = fields.One2many('fsm.person',
                                       'mail_compose_wiz',
                                       string="Recipients"
                                       )
    subject = fields.Char(string="Subject")
    body = fields.Html(string="Body")
    notify_type = fields.Char()

    @api.onchange('notify_type')
    def onchange_notify_type(self):
        """
        We will load the values for this model based on
        the notify_type(customer or employee).
        The default mail template and
        recipients list may change according to the
        notify_type value.
        """
        notify_type = self._context.get('default_notify_type')
        # getting current ticket
        if self._context.get('active_model') == 'fsm.support.ticket':
            ticket_id = self._context.get('active_id')
            rec = self.env['fsm.support.ticket'].browse(ticket_id)

        if not rec:
            raise exceptions.UserError(_('Exception occured !'))

        rec.ensure_one()
        if notify_type == 'customer':
            # mail notification to customer
            if not rec.customer_id:
                # making sure there is a customer selected
                raise exceptions.ValidationError(
                    'Please Select a Customer First!')
            # selecting template
            template = self.env.ref(
                'fsm_support_ticket.notify_customer_mail',
                False)
            # setting default recipient
            self.recipient = rec.customer_id.ids if rec.customer_id else None
        if notify_type == 'employee':
            # notification to assigned person or serviceman
            template = self.env.ref(
                'fsm_support_ticket.notify_employee_mail',
                False)
            # setting recipient
            self.recipient_person = rec.person_id.ids

        # setting mail subject, body, etc.
        self.email_from = self.env.user.partner_id.email
        self.subject = "Ticket Status"
        self.body = template.body_html

    @api.multi
    def send_status(self):
        """This function will collect all the values provided
        in the wizard and sends mail to corresponding recipients."""
        mail_from = self.email_from
        model_obj = self.env['ir.model.data']
        # collecting all the recipients, there may be multiple recipients
        email_str = ''
        if self.notify_type == 'customer':
            template_id = \
                model_obj.get_object_reference('fsm_support_ticket',
                                               'notify_customer_mail'
                                               )[1]
            for rec in self.recipient:
                email_str += rec.email + "," if rec.email else ''
            email_str = email_str[:-1]
        else:

            template_id = \
                model_obj.get_object_reference('fsm_support_ticket',
                                               'notify_employee_mail'
                                               )[1]
            for rec in self.recipient_person:
                email_str += rec.email + "," if rec.email else ''
            email_str = email_str[:-1]

        # obtaining the template for sending the mail

        template = self.env['mail.template'].browse([template_id])
        # generating mail
        values = template.generate_email(self.id)

        # setting from address , to address and mail content
        values['email_to'] = email_str
        values['email_from'] = mail_from
        values['body_html'] = self.body
        values['res_id'] = False
        # sending mail, if everything is ok
        if values['email_to'] and values['email_from']:
            mail_mail_obj = self.env['mail.mail']
            msg_id = mail_mail_obj.sudo().create(values)
            if msg_id:
                msg_id.send()
                if self.notify_type == 'employee':
                    # Updating the stage of ticket after sending mail
                    # setting the stage to 'Sent to Employee'

                    # getting current ticket
                    rec = None
                    if self._context.get('active_model') == \
                            'fsm.support.ticket':
                        ticket_id = self._context.get('active_id')
                        rec = self.env['fsm.support.ticket'].browse(ticket_id)

                    if rec:
                        rec.state = 'sent_to_employee'

        # now we need to send notifications to
        # all the recipients(private channel)
        # so if there is no channel exists, we will create one
        # gathering all the partner details
        partner_ids = {}
        user = self.env.user
        partner_ids[user.partner_id.id] = []
        try:
            for emp in self.recipient_person:
                if emp.partner_id:
                    partner_ids[emp.partner_id.id] = []
            for customer in self.recipient:
                partner_ids[customer.id] = []
        except Exception as e:
            pass
        # we got the partner ids, now we check for channels
        cr = self._cr
        channel_partners = None
        if partner_ids.keys():
            cr.execute("SELECT partner_id,channel_id "
                       "FROM mail_channel_partner "
                       "WHERE "
                       "partner_id in %s and channel_id is not null ",
                       (tuple(partner_ids.keys()), ))
            channel_partners = cr.dictfetchall()
        for rec in channel_partners:
            partner_ids[rec['partner_id']].append(rec['channel_id']) \
                if rec['channel_id'] not in partner_ids[rec['partner_id']] \
                else None

        # now fetch the channels to which we need to send message to
        channels_to_update = []
        sender_channels = partner_ids.pop(user.partner_id.id)
        for i in partner_ids:
            create_channel = True
            for channel_id in partner_ids[i]:
                if channel_id in sender_channels:
                    create_channel = False
                    channels_to_update.append(channel_id) \
                        if channel_id not in channels_to_update \
                        else None
                    break
            # there is no channel for this partner and sender,
            # so we are creating a direct channel
            if create_channel:
                partner = self.env['res.partner'].browse(i)
                channel_name = partner.name + ", " + user.partner_id.name
                try:
                    channel_id = self.env['mail.channel'].create({
                        'name': channel_name,
                        'public': 'private',
                        'channel_type': 'chat',
                        'channel_partner_ids': [
                            (6, 0, [i, user.partner_id.id])]
                    })
                    channels_to_update.append(channel_id.id)\
                        if channel_id else None
                except Exception:
                    pass

        # sending the message directly
        # to the recipient channel
        # here the channel is a direct channel
        # which inludes the sender and recipient
        self.env['mail.message'].create({
            'message_type': 'notification',
            'body': self.body,
            'channel_ids': [(6, 0, channels_to_update)]
        })

        return False
