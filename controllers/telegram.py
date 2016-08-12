import openerp.http as http
from openerp.http import request, SUPERUSER_ID
import logging, pdb
from datetime import datetime
_logger = logging.getLogger(__name__)
account=False
class MyController(http.Controller):

    @http.route('/sms/telegram/receipt', type="http", auth="public")
    def sms_telegram_receipt(self, **kwargs):
        values = {}
	for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        
        request.env['esms.telegram'].sudo().delivary_receipt(values['AccountSid'], values['MessageSid'])
        
        return "<Response></Response>"
        
    @http.route('/sms/telegram/receive/<telegram_token>/', type="json", auth="public")
    def sms_telegram_receive(self, telegram_token):
        account=request.env['esms.accounts'].sudo().search([('telegram_token','=',telegram_token)])
        if len(account)==1:
            request.env['esms.telegram'].sudo().receive_message(account,request.jsonrequest)
            return {"ok":True,"error code":200,"description":"ok"}
        else:
            return {"ok":False,"error code":404,"description":"Token unknown"}
            
