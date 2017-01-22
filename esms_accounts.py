from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests
from datetime import datetime
import pdb

class esms_accounts(models.Model):

    _name = "esms.accounts"
    _order ="priority asc"
    
    name = fields.Char(required=True, string='Account Name')
    account_gateway = fields.Many2one('esms.gateways', required=True)
    gateway_model = fields.Char(related="account_gateway.gateway_model_name")
    priority = fields.Integer(string="Priority", default="100")
    poll=fields.Boolean(help="Include this account in poll cycle?", default=False)
    keep_alive=fields.Boolean(help="Send keep alive messages", default=False)
    keep_alive_minutes=fields.Integer(help="Keep alive interval", default=60)
    keep_alive_timeout=fields.Integer(help="Keep alive timeout", default=5)
    keep_alive_string=fields.Char(help="String to begin keepalive message, eg for routing purposes")
    last_keep_alive_sent=fields.Datetime()
    last_keep_alive_received=fields.Datetime()
    keep_alive_partner_id=fields.Many2one('res.partner')
    keep_alive_sender=fields.Many2one('esms.verified.numbers', domain="[('account_id','=', id)]")
    keep_alive_problem=fields.Boolean(default=False)

    @api.model
    def check_all_messages(self):                
        my_accounts = self.env['esms.accounts'].search([('priority','>=',0)])
        for sms_account in my_accounts:    
            if sms_account.poll and hasattr(self.env[sms_account.account_gateway.gateway_model_name], 'check_messages'):
                self.env[sms_account.account_gateway.gateway_model_name].check_messages(sms_account.id)

    @api.multi
    def check_messages(self):                
        #my_accounts = self.env['esms.accounts'].search([('priority','>',0)])    
        for sms_account in self:            
            if hasattr(self.env[sms_account.account_gateway.gateway_model_name], 'check_messages'):
                self.env[sms_account.account_gateway.gateway_model_name].check_messages(sms_account.id)
    @api.multi
    def send_keep_alive(self):
        #pdb.set_trace()
        self.last_keep_alive_sent=fields.Datetime.now()
        self.env[self.gateway_model].send_message(self.id, 
         self.keep_alive_sender.mobile_number,
         self.keep_alive_partner_id.mobile, self.keep_alive_string + " " + self.last_keep_alive_sent, 
         None,None,None)
        _logger.info ("Keep alive sent")
  

    @api.model
    def process_keep_alive(self):                
        my_accounts = self.env['esms.accounts'].search([('priority','>=',0),('keep_alive','=',True)])
        for account in my_accounts:
            if account.keep_alive_minutes < ((datetime.strptime(fields.Datetime.now(),"%Y-%m-%d %H:%M:%S") - datetime.strptime(account.last_keep_alive_sent,"%Y-%m-%d %H:%M:%S")).seconds/60):
                account.send_keep_alive()
            #pdb.set_trace()
            if (account.keep_alive_timeout < ((datetime.strptime(fields.Datetime.now(),"%Y-%m-%d %H:%M:%S") - datetime.strptime(account.last_keep_alive_received,"%Y-%m-%d %H:%M:%S")).seconds/60)):
                if not account.keep_alive_problem:
                    _logger.info ("SMS Keep alive timeout")
                    account.keep_alive_problem=True
                    account.keep_alive_partner_id.message_post(body="Missing keepalive, time in UTC!",
                        subject="[Problem] Last keepalive received: " + account.last_keep_alive_received,
                        type = 'comment',
                        subtype = "mail.mt_comment")
            else:
                if account.keep_alive_problem:
                    account.keep_alive_partner_id.message_post(body="Keepalive repaired, time in UTC!",
                        subject="[Repaired] Last keepalive received: " + account.last_keep_alive_received,
                        type = 'comment',
                        subtype = "mail.mt_comment")
                    account.keep_alive_problem=False








    @api.multi
    def set_webhook(self):   
        if hasattr(self.env[self.account_gateway.gateway_model_name], 'set_webhook'):
            self.env[self.account_gateway.gateway_model_name].set_webhook(self)
    
