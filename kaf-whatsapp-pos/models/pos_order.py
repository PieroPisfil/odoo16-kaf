# -*- coding: utf-8 -*-

from odoo import fields, models, api
import base64
import io
# from odoo.exceptions import UserError, ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    whatsapp_api_url = fields.Char(string='URL de app', related='company_id.whatsapp_api_url')
    whatsapp_key = fields.Integer(string='Key de app', related='company_id.whatsapp_key')
    whatsapp_token = fields.Char(string='Token de app', related='company_id.whatsapp_token')

    def send_ticket_whatsapp(self, phonenumber, ordername, partner, ticket):
        res = {'error': True, 'message': 'No Enviado, error de comunicación con api', 'data': {}}
        endpoint = "{0}/message/image?key={1}".format(self.whatsapp_api_url, self.whatsapp_key)
        imagen = io.BytesIO(base64.b64decode(ticket))    
        files = [("file", ('icon.jpg', imagen, 'image/jpeg'))]
        headers = {}
        data = {
            "id": "%s" % phonenumber,
            "caption" : "Gracias por su compra %s. Referencia: Número de %s." % (partner['name'], ordername),
        }
        try:
            # 
            result = requests.request("POST", endpoint, headers=headers, data=data, files=files, timeout = (3, 5))
            result_json = result.json()
            if not result_json['error']:
                res = {'error': False, 'message': 'Ok Enviado', 'data': result_json['data']}
            else:
                res = {'error': True, 'message': result_json['message'], 'data': {}}
            _logger.info('***************response: {0}'.format(res))
            return res
        except Exception:
            _logger.exception("+++++++++++Falla al tratar de obtener datos de %r", endpoint)
            return res