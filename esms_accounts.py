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

    @api.model
    def check_all_messages(self):                
        my_accounts = self.env['esms.accounts'].search([('priority','>=',0)])
        for sms_account in my_accounts:    
            if self.poll and hasattr(self.env[sms_account.account_gateway.gateway_model_name], 'check_messages'):
                self.env[sms_account.account_gateway.gateway_model_name].check_messages(sms_account.id)

    @api.multi
    def check_messages(self):                
        #my_accounts = self.env['esms.accounts'].search([('priority','>',0)])    
        for sms_account in self:            
            if hasattr(self.env[sms_account.account_gateway.gateway_model_name], 'check_messages'):
                self.env[sms_account.account_gateway.gateway_model_name].check_messages(sms_account.id)

    @api.multi
    def set_webhook(self):   
        if hasattr(self.env[self.account_gateway.gateway_model_name], 'set_webhook'):
            self.env[self.account_gateway.gateway_model_name].set_webhook(self)
    
