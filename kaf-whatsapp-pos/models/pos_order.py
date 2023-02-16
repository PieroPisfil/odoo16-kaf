# -*- coding: utf-8 -*-

from odoo import fields, models, api
import json
import base64
import io
from PIL import Image
from odoo.exceptions import UserError, ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    whatsapp_api_url = fields.Char(string='URL de app', related='company_id.whatsapp_api_url')
    whatsapp_key = fields.Char(string='Key de app', related='company_id.whatsapp_key')
    whatasapp_token = fields.Char(string='Token de app', related='company_id.whatasapp_token')
    whatsapp_qr = fields.Char(related='company_id.whatsapp_qr', store=True)

    def send_ticket_whatsapp(self, phonenumber, ordername, partner, ticket):
        res = {'error': True, 'message': 'No Enviado', 'data': {}}
        endpoint = "{0}/message/image?key={1}".format(self.whatsapp_api_url, self.whatsapp_key)
        imagen = io.BytesIO(base64.b64decode(ticket))    
        files = [("file", ('icon.jpg', imagen, 'image/jpeg'))]
        headers = {}
        body = {}
        data = {
            "id": "%s" % phonenumber,
            "caption" : "Gracias por su compra %s. Referencia: Número de %s." % (partner['name'], ordername),
        }
        # _logger.info('***************response: {0}'.format(endpoint))
        result = requests.post(endpoint, headers=headers, data=data, json = body, files=files)
        
        if result.status_code == 200 or 201:
           result_json = result.json()
           if not result_json['error']:
               res = {'error': False, 'message': 'Ok Enviado', 'data': {}}
               return res
        return res