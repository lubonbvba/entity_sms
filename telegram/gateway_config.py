from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests
from datetime import datetime
from time import gmtime, strftime
import json
import pdb

class sms_response():
     response_string = ""
     response_code = ""
     human_read_error = ""
     message_id = ""
     delivary_state = ""

class telegram_core(models.Model):

    _name = "esms.telegram"
    
    api_url = fields.Char(string='API URL', default="https://api.telegram.org")
    
    def send_message(self, sms_gateway_id,from_number,to_number, sms_content, my_model_name, my_record_id, my_field_name):
        sms_account = self.env['esms.accounts'].search([('id','=',sms_gateway_id)])
       
        format_number = to_number
        if " " in format_number: format_number.replace(" ", "")
        if "+" in format_number: format_number = format_number.replace("+", "")
   #     telegram_url = "http://api.telegram.com/http/sendmsg?user=" + str(sms_account.telegram_username) + "&password=" + str(sms_account.telegram_password) + "&api_id=" + str(sms_account.telegram_api_id) + "&from=" + str(self.env.user.partner_id.mobile) + "&to=" + str(format_number) + "&text=" + str(sms_content)

        telegram_url="https://api.telegram.org/" + str(sms_account.telegram_api_id) + "/sendMessage" 
        telegram_url+="?chat_id=" + str(to_number)
        telegram_url+="&text=" + str(sms_content)
        response_string = requests.get(telegram_url)
        #pdb.set_trace()

        response_code = ""
        if "ERR: 002" in response_string.text:
	    response_code = "BAD CREDENTIALS"
	elif "ERR: 301" in response_string.text:
	    response_code = "INSUFFICIENT CREDIT"
	elif "ERR:" in response_string.text:
	    response_code = "FAILED DELIVERY"
	else:
	    response_code = "SUCCESSFUL"
        
        #pdb.set_trace()   
        
        my_model = self.env['ir.model'].search([('model','=',my_model_name)])
        my_field = self.env['ir.model.fields'].search([('name','=',my_field_name)])
        
        if response_code == "SUCCESSFUL":
            esms_history = self.env['esms.history'].create({'field_id':my_field[0].id, 'record_id': my_record_id,'model_id':my_model[0].id,'account_id':sms_account.id,'from_mobile':self.env.user.partner_id.mobile, 'to_mobile':to_number,'sms_content':sms_content,'status_string':response_string.text, 'direction':'O','my_date':datetime.utcnow(), 'status_code':'successful'})
        
        my_sms_response = sms_response()
        my_sms_response.response_string = response_string.text
        my_sms_response.response_code = response_code
        
        return my_sms_response
       
    def check_messages(self, account_id=None, message_id=""):
        #pdb.set_trace()
        if not account_id:
            account_id=self.env.context['active_id']
        sms_account = self.env['esms.accounts'].browse(account_id)
        telegram_url="https://api.telegram.org/" + str(sms_account.telegram_api_id) + "/getUpdates" 
        response_string = requests.get(telegram_url)
        response=json.loads(response_string.content)
        for message in response['result']:
            if len(self.env['esms.history'].search([('sms_gateway_message_id','=',message['update_id'])])) == 0:
                vals={
                    'sms_gateway_message_id':message['update_id'],
                    'account_id': account_id,
                    'direction': 'I',
                    'status_string': str(message),
                    'from_mobile':message['message']['from']['id'],
                    'to_mobile':sms_account['name'],
                    'my_date':strftime("%Y-%m-%d %H:%M:%S", gmtime(message['message']['date']))
                    }
                if 'text' in message['message'].keys():
                    vals.update({
                        'sms_content': message['message']['text'],
                    })
               # pdb.set_trace()

                history_id = self.env['esms.history'].create(vals)



class telegram_conf(models.Model):

    _inherit = "esms.accounts"
    
    telegram_api_id = fields.Char(string='API ID')