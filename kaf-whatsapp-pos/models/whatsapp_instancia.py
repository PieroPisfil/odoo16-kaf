# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import logging
import requests
import time

_logger = logging.getLogger(__name__)

class WhatsappInstancia(models.Model):
    _name = "whatsapp.instancia"

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name,active)',  'Dos instancias no deben tener el mismo nombre!')
    ]

    name = fields.Integer(string='Nro. de instancia',copy=False,required=True,)
    state = fields.Selection([
        ('borrador','Borrador'),
        ('activa','Activa'),
        ('logout','Sesión cerrada'),
        ('eliminada','Elimnado'),
    ],copy=False, default='borrador',string='Estado')
    info_instancia_rspta = fields.Char(copy=False)
    numero_telefono = fields.Char(string='Nro. de telefono',copy=False)
    # qr_b64 = fields.Char(string='QR codigo',copy=False,readonly=True)
    qr_b64 = fields.Html(string='QR codigo',copy=False,readonly=True,translate=False)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    active = fields.Boolean(default=True, copy=False)
    instancias_listadas = fields.Char()
    # image = fields.Binary(string='Image',copy=False,readonly=True)

    def button_activar_instancia_wa(self):
        endpoint = "{0}/instance/init?key={1}&token={2}".format(self.company_id.whatsapp_api_url, self.name, self.company_id.whatasapp_token)
        payload = ""
        headers = {}
        try:
            response = requests.request("GET", endpoint, headers=headers, data=payload, timeout = (3, 5))
            result_json = response.json()
            if response.status_code == 200:
                #_logger.info('****************************** {}'.format(response.text))
                self.info_instancia_rspta = result_json
                if not result_json['error']:
                    self.state = 'activa'
                    time.sleep(1)
                    self.button_obtener_qr()
        except Exception:
            _logger.exception("Falla al tratar de obtener datos de %r", endpoint)
            return None

    def button_logout_instancia_wa(self):
        endpoint = "{0}/instance/logout?key={1}&token={2}".format(self.company_id.whatsapp_api_url, self.name, self.company_id.whatasapp_token)
        payload = ""
        headers = {}
        try:
            response = requests.request("DELETE", endpoint, headers=headers, data=payload, timeout = (3, 5))
            result_json = response.json()
            if response.status_code == 200:
                #_logger.info('****************************** {}'.format(response.text))
                self.info_instancia_rspta = result_json
                if not result_json['error']:
                    self.state = 'logout'
            elif result_json['error']:
                self.state = 'borrador'
            self.numero_telefono = ''
            self.qr_b64 = ''
        except Exception:
            _logger.exception("Falla al tratar de obtener datos de %r", endpoint)
            return None

    def button_eliminar_instancia_wa(self):
        endpoint = "{0}/instance/delete?key={1}".format(self.company_id.whatsapp_api_url, self.name)
        payload = ""
        headers = {}
        try:
            response = requests.request("DELETE", endpoint, headers=headers, data=payload, timeout = (3, 5))
            result_json = response.json()
            if response.status_code == 200:
                #_logger.info('****************************** {}'.format(response.text))
                self.info_instancia_rspta = result_json
                if not result_json['error']:
                    self.state = 'eliminada'
            elif result_json['error']:
                self.state = 'borrador'
            self.numero_telefono = ''
            self.qr_b64 = ''
        except Exception:
            _logger.exception("Falla al tratar de obtener datos de %r", endpoint)
            return None

    def button_borrador_instancia_wa(self):
        self.state = 'borrador'
        self.numero_telefono = ''
        self.qr_b64 = ''
        self.button_instancia_info()

    def button_instancia_info(self):
        endpoint = "{0}/instance/info?key={1}".format(self.company_id.whatsapp_api_url, self.name)
        payload = ""
        headers = {}
        try:
            response = requests.request("GET", endpoint, headers=headers, data=payload, timeout = (3, 5))
            result_json = response.json()
            if response.status_code == 200 or 403:
                self.info_instancia_rspta = result_json
                if result_json['error'] and result_json['message'] == "invalid key supplied":
                    self.state = 'borrador'
                elif not result_json['error']:
                    self.numero_telefono = result_json['instance_data']['user']['id'].split(":")[0]

        except Exception:
            _logger.exception("Falla al tratar de obtener datos de %r", endpoint)
            return None

    def button_listar_sesiones(self):
        endpoint = "{0}/instance/list".format(self.company_id.whatsapp_api_url)
        payload={}
        headers = {}
        try:
            response = requests.request("GET", endpoint, headers=headers, data=payload, timeout = (3, 5))
            result_json = response.json()
            if response.status_code == 200:
                self.instancias_listadas = result_json
        except Exception:
            _logger.exception("Falla al tratar de obtener datos de %r", endpoint)
            return None
    
    def button_obtener_qr(self):
        endpoint = "{0}/instance/qr?key={1}&token={2}".format(self.company_id.whatsapp_api_url, self.name, self.company_id.whatasapp_token)
        payload = ""
        headers = {}
        try:
            response = requests.request("GET", endpoint, headers=headers, data=payload, timeout = (3, 5))
            #result_json = response.json()
            result_json = response.text
            self.qr_b64 = ''
            if response.status_code == 200:
                #if not result_json['error']:
                if result_json:
                    #self.qr_b64 = result_json['qrcode']
                    self.qr_b64 = result_json
        except Exception:
            _logger.exception("Falla al tratar de obtener datos de %r", endpoint)
            return None