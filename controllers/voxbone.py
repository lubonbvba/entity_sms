import openerp.http as http
from openerp.http import request, SUPERUSER_ID
import logging, pdb
from datetime import datetime
_logger = logging.getLogger(__name__)

class MyController(http.Controller):

    @http.route('/sms/voxbone/receipt', type="http", auth="public")
    def sms_voxbone_receipt(self, **kwargs):
        values = {}
        pdb.set_trace()
	for field_name, field_value in kwargs.items():
            values[field_name] = field_value
        
        request.env['esms.voxbone'].sudo().delivery_receipt(values['AccountSid'], values['MessageSid'])
        
        return "<Response></Response>"
        
    @http.route('/sms/voxbone/receive/<number>/', type="json", auth="public")
    def sms_voxbone_receive(self, number):
        #pdb.set_trace()
           
        request.env['esms.voxbone'].sudo().receive_message(number,request.jsonrequest)
        
        return 200