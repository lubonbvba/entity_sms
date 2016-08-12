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
        
    @http.route('/sms/telegram/receive/<account>/', type="json", auth="public")
    def sms_telegram_receive(self, account):
        
        #pdb.set_trace()   
        request.env['esms.telegram'].sudo().receive_message(account,request.jsonrequest)
        
        return 200