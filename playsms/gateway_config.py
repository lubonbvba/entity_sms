from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests, json
from datetime import datetime
from time import gmtime, strftime
import pdb

class sms_response():
     response_string = ""
     response_code = ""
     human_read_error = ""
     delivery_state = ""
     message_id = ""

class playsms_core(models.Model):

    _name = "esms.playsms"
    
    api_url = fields.Char(string='API URL')
    
    def send_message(self, sms_gateway_id, from_number, to_number, sms_content, my_model_name, my_record_id, my_field_name):
        sms_account = self.env['esms.accounts'].search([('id','=',sms_gateway_id)])
       
        format_number = to_number
        if " " in format_number: format_number.replace(" ", "")
    #    if "+" in format_number: format_number = format_number.replace("+", "")
        playsms_url=sms_account.playsms_baseurl + "/index.php?app=ws&op=pv&u=" + sms_account.playsms_username + "&h="  + sms_account.playsms_api_token
        playsms_url +=  "&to=" + str(format_number) + "&msg=" + str(sms_content)
        #pdb.set_trace()
       
        response_string = requests.get(playsms_url)
        response_json=json.loads(response_string.content)
        response_code = ""

        my_model = self.env['ir.model'].search([('model','=',my_model_name)])
        my_field = self.env['ir.model.fields'].search([('name','=',my_field_name)])
        history= {
                'field_id':my_field[0].id, 
                'record_id': my_record_id,
                'model_id':my_model[0].id,
                'account_id':sms_account.id,
                'from_mobile':from_number,
                'to_mobile':to_number,
                'sms_content':sms_content,
                'status_string':response_string.text,
                'direction':'O','my_date':datetime.utcnow(),

        }
        if response_json['error_string'] == None:
            response_code = "SUCCESSFUL"
            history['status_code']='successful'
            history['sms_gateway_message_id']=response_json['data'][0]['queue']
        else:
            response_code = "FAILED DELIVERY"
            history['status_code']='failed'

#        pdb.set_trace()   
        

#        if response_code == "SUCCESSFUL":
        esms_history = self.env['esms.history'].create(history)
        
        my_sms_response = sms_response()
        my_sms_response.response_string = response_json['error_string']
        my_sms_response.response_code = response_code
        my_sms_response.delivery_state = history['status_code']
        
        return my_sms_response

    
    def check_messages(self, account_id=None, message_id=""):

        if not account_id:
            account_id=self.env.context['active_id']
        sms_account = self.env['esms.accounts'].browse(account_id)

        playsms_url=sms_account.playsms_baseurl + "/index.php?app=ws&op=ix&u=" + sms_account.playsms_username + "&h="  + sms_account.playsms_api_token

        response_string = requests.get(playsms_url)
        response=json.loads(response_string.content)
 
        self.receive_message(sms_account,response)
     


    def receive_message(self,sms_account,response): 
#        vals={'status_string': str(response)}
        if ('data' in response.keys()):
            for message in response['data']:
                if len(self.env['esms.history'].search([('sms_gateway_message_id','=',message['id'])])) == 0:
                    vals={
                    'sms_gateway_message_id':message['id'],
                    'account_id': sms_account.id,
                    'direction': 'I',
                    'status_string': str(message),
                    'from_mobile':message['src'],
                    'to_mobile':message['dst'],
                    'my_date': message['dt'],
                    'sms_content': message['msg'],
                    }
                    history_id = self.env['esms.history'].create(vals)
        else:
            history_id = self.env['esms.history'].create({'status_string': str(response)})




class playsms_conf(models.Model):

    _inherit = "esms.accounts"
    
    playsms_username = fields.Char(string='API Username')
    playsms_baseurl = fields.Char(string='Base url')
    playsms_api_token = fields.Char(string='API Token')
    playsms_send_additional = fields.Char(string='Additional parameters')
    playsms_footer = fields.Char(string='Footer on', default=True)