from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests
from datetime import datetime


class res_company_esms(models.Model):

    _inherit = "res.company"
    esms_default_sender=fields.Many2one('esms.verified.numbers')