import openerp.http as http
from openerp.http import request, SUPERUSER_ID
import logging, pdb
from datetime import datetime
_logger = logging.getLogger(__name__)

class MyController(http.Controller):

    @http.route('/sms/telegram/receipt', type="http", auth="public")
    def sms_telegram_receipt(self, **kwargs):
        values = {}
	for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        
        request.env['esms.telegram'].sudo().delivary_receipt(values['AccountSid'], values['MessageSid'])
        
        return "<Response></Response>"
        
    @http.route('/sms/telegram/receive/<number>/', type="json", auth="public")
    def sms_telegram_receive(self, number):
        pdb.set_trace() 
        values = {}
	for field_name, field_value in kwargs.items():
            values[field_name] = field_value
           
        
        telegram_account = request.env['esms.accounts'].sudo().search([('telegram_account_sid','=', values['AccountSid'])])
        request.env['esms.telegram'].sudo().check_messages(telegram_account.id, values['MessageSid'])
        
        return "<Response></Response>"