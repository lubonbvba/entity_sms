import openerp.http as http
from openerp.http import request, SUPERUSER_ID
import logging, pdb
from datetime import datetime
_logger = logging.getLogger(__name__)

class MyController(http.Controller):

    @http.route('/sms/gsmmodem/receipt', type="http", auth="public")
    def sms_voxbone_receipt(self, **kwargs):
        values = {}
	for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        
        request.env['esms.gsmmodem'].sudo().delivary_receipt(values['AccountSid'], values['MessageSid'])
        
        return "<Response></Response>"
        
    @http.route('/sms/gsmmodem/receive', type="http", auth="public")
    def sms_gsmmodem_receive(self, **kwargs):
        values = {}
        for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        #pdb.set_trace()   
        request.env['esms.gsmmodem'].sudo().receive_message(values)
        
        return "<Response></Response>"