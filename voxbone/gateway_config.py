from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests
from datetime import datetime
from time import gmtime, strftime
import json
import pdb
from requests.auth import HTTPDigestAuth

class sms_response():
     response_string = ""
     response_code = ""
     human_read_error = ""
     message_id = ""
     delivery_state = ""

class voxbone_core(models.Model):

    _name = "esms.voxbone"
    
    api_url = fields.Char(string='API URL', default="https://api.voxbone.org")

    
    def send_message(self, sms_gateway_id,from_number,to_number, sms_content, my_model_name, my_record_id, my_field_name,partner_id=None):
        sms_account = self.env['esms.accounts'].search([('id','=',sms_gateway_id)])
       
        format_number = to_number
        if " " in format_number: format_number.replace(" ", "")
        if "+" in format_number: format_number = format_number.replace("+", "")
        voxbone_url=sms_account.voxbone_url + format_number
        body={
            'from':from_number,
            'msg': sms_content,
            'delivery_report': 'none',
        }
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.post(voxbone_url,
            auth=HTTPDigestAuth(sms_account.voxbone_user,sms_account.voxbone_password),
            json=body,
            headers=headers)

        response_code = ""
        if "202" in response.text:
            response_code = "SUCCESSFUL"
        else:
            response_code = "UNKNOWN"
        
        #pdb.set_trace()   
        
        my_model = self.env['ir.model'].search([('model','=',my_model_name)])
        my_field = self.env['ir.model.fields'].search([('name','=',my_field_name)])
        if my_model_name=='res.partner':
            partner_id=my_record_id
        #pdb.set_trace()      
        #if response_code == "SUCCESSFUL":
        esms_history = self.env['esms.history'].create({
            'field_id':my_field[0].id,
            'record_id': my_record_id,
            'model_id':my_model[0].id,
            'account_id':sms_account.id,
            'from_mobile':from_number,
            'to_mobile':to_number,
            'sms_content':sms_content,
            'status_string':response.reason,
            'direction':'O',
            'my_date':datetime.utcnow(),
            'status_code':'successful',
            'partner_id':partner_id
            })

        if 'transaction_id' in response.json().keys():
            esms_history.write({
                'sms_gateway_message_id':response.json()['transaction_id']
                })

        #pdb.set_trace()
        my_sms_response = sms_response()
        my_sms_response.response = response.reason
        my_sms_response.response_code = response_code
        
        return my_sms_response
       
    def check_messages(self, account_id=None, message_id=""):
        #pdb.set_trace()
        if not account_id:
            account_id=self.env.context['active_id']
        sms_account = self.env['esms.accounts'].browse(account_id)
        voxbone_url="https://api.voxbone.org/" + str(sms_account.voxbone_api_id) + "/getUpdates" 
        response_string = requests.get(voxbone_url)
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
    def receive_message(self,number,vals):
        if self.env['esms.verified.numbers'].search([('mobile_number','=', number)]).account_id.id:
            self.env['esms.history'].create({
                'sms_content':vals['msg'],
                'to_mobile':number,
                'direction': 'I',
                'my_date': vals['time'],
                'from_mobile':vals['from'],
                'status_string': str(vals),
                'sms_gateway_message_id': vals['uuid'],
                'account_id': self.env['esms.verified.numbers'].search([('mobile_number','=', number)]).account_id.id,
                })
        else:
            #no account found
            _logger.info("No account found for voxbone number: %s" % (number))


class voxbone_conf(models.Model):

    _inherit = "esms.accounts"
    
    voxbone_url= fields.Char(default="https://sms.voxbone.com:4443/sms/v1/")
        
    voxbone_user=fields.Char()
    voxbone_password=fields.Char()


