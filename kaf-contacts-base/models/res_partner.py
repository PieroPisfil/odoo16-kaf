# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)


state_sunat_v = [('ACTIVO', 'ACTIVO'),
                 ('BAJA DE OFICIO', 'BAJA DE OFICIO'),
                 ('BAJA DEFINITIVA', 'BAJA DEFINITIVA'),
                 ('BAJA PROVISIONAL', 'BAJA PROVISIONAL'),
                 ('SUSPENSION TEMPORAL', 'BAJA PROVISIONAL'),
                 ('INHABILITADO-VENT.UN', 'INHABILITADO-VENT.UN'),
                 ('BAJA MULT.INSCR. Y O', 'BAJA MULT.INSCR. Y O'),
                 ('PENDIENTE DE INI. DE', 'PENDIENTE DE INI. DE'),
                 ('OTROS OBLIGADOS', 'OTROS OBLIGADOS'),
                 ('NUM. INTERNO IDENTIF', 'NUM. INTERNO IDENTIF'),
                 ('ANUL.PROVI.-ACTO ILI', 'ANUL.PROVI.-ACTO ILI'),
                 ('ANULACION - ACTO ILI', 'ANULACION - ACTO ILI'),
                 ('BAJA PROV. POR OFICI', 'BAJA PROV. POR OFICI'),
                 ('ANULACION - ERROR SU', 'ANULACION - ERROR SU')]

condition_sunat_v = [('HABIDO', 'HABIDO'),
                     ('NO HABIDO', 'NO HABIDO'),
                     ('NO HALLADO', 'NO HALLADO'),
                     ('PENDIENTE', 'PENDIENTE'),
                     ('NO HALLADO SE MUDO D', 'NO HALLADO SE MUDO D'),
                     ('NO HALLADO NO EXISTE', 'NO HALLADO NO EXISTE'),
                     ('NO HALLADO FALLECIO', 'NO HALLADO FALLECIO'),
                     ('-', 'NO HABIDO'),
                     ('NO HALLADO OTROS MOT', 'NO HALLADO OTROS MOT'),
                     ('NO APLICABLE', 'NO APLICABLE'),
                     ('NO HALLADO NRO.PUERT', 'NO HALLADO NRO.PUERT'),
                     ('NO HALLADO CERRADO', 'NO HALLADO CERRADO'),
                     ('POR VERIFICAR', 'POR VERIFICAR'),
                     ('NO HALLADO DESTINATA', 'NO HALLADO DESTINATA'),
                     ('NO HALLADO RECHAZADO', 'NO HALLADO RECHAZADO')]

# QUERY PARA APIS PERU
QUERY_DOCUMENT_APISPERU = {
    'urls': {
        'dni': 'https://dniruc.apisperu.com/api/v1/dni/{vat}?token={token}',
        'ruc': 'https://dniruc.apisperu.com/api/v1/ruc/{vat}?token={token}'
    }
}
class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Modificamos para que aparezca Perú por defecto
    country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict', default=lambda self: self.env.ref('base.pe'))
    # country_codigo = fields.Char(related='country_id.code', store=True)
    # Modificamos para que aparezca Lambayeque por defecto
    # state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
    #                           domain="[('country_id', '=?', country_id)]", default=lambda self: self.env.ref('base.state_pe_14'))

    l10n_pe_district = fields.Many2one('l10n_pe.res.city.district', string='District', help='Districts are part of a province or city.',
                                       default=lambda self: self._search_district())
    # Modificamos para que aparezca RUC por defecto
    l10n_latam_identification_type_id = fields.Many2one(
        'l10n_latam.identification.type', default=lambda self: self.env.ref('l10n_pe.it_RUC'))
    commercial_name = fields.Char(
        string='Nombre comercial', default='-', copy=False)
    legal_name = fields.Char(string='Nombre legal', default='-', copy=False)
    state_sunat = fields.Selection(
        state_sunat_v, string='Estado', default='ACTIVO', copy=False)
    condition_sunat = fields.Selection(
        condition_sunat_v, string='Condición', default='HABIDO', copy=False)
    is_validate = fields.Boolean(string='Está validado', copy=False)

    last_update = fields.Datetime(string='Última actualización', copy=False)

    company_id = fields.Many2one(
        'res.company', default=lambda self: self._search_company())

    zip = fields.Char(related='l10n_pe_district.code', store=True)
    # Verificamos que no haya doscontactos con el mismo dni, ruc o pasaporte
    _sql_constraints = [
        ('unique_vat', 'unique(vat, active, name, street)',
         'Error: El usuario ya está registrado, (tal vez en otra compañía, verificarlo y hacerlo multicompañía)')
    ]

    @api.onchange('company_type')
    def _on_change_estado(self):
        if self.company_type == 'person' and not self.vat:
            self.l10n_latam_identification_type_id = self.env.ref(
                'l10n_pe.it_DNI')
        if self.company_type == 'company':
            self.l10n_latam_identification_type_id = self.env.ref(
                'l10n_pe.it_RUC')

    @api.onchange('country_id')
    def _on_change_country_id(self):
        if self.country_id and self.country_id.code != 'PE':
            self.l10n_pe_district = None
            self.city_id = None

    @api.model
    def consulta_vat_existe(self, nro_documento, format='json'):
        #res_partner = self.search([('vat', '=', nro_documento), ('active', '=', True)]).exists()
        query = """ SELECT vat FROM res_partner WHERE vat = '%s' AND active""" % (nro_documento)
        self._cr.execute(query)
        res_2 = self.env.cr.dictfetchall()
        #_logger.info('***************response: {0}'.format(res_2))
        if res_2 : 
            res = {'error': True, 'message': 'Hay otro contacto con este Nro de Documento aquí o en otra compañia. Si es adrede, llamar al Administrador del sistema para hacer el contacto multiempresa desde módulo de contactos. Pasar como dato el Nro de Documneto/RUC/DNI.'} 
            return res
        else : 
            res = {'error': False, 'message': 'Nohaycoincidencias'}
            return res
            
    @api.model
    def consulta_datos(self, tipo_documento, nro_documento, format='json'):
        res = {'error': True, 'message': 'Error de consulta, puede que el ruc este inactivo.', 'data': {}}
        # Si el nro. de doc. ya existe
        res_partner = self.search([('vat', '=', nro_documento), ('active', '=', True)]).exists()
        if res_partner:
           res['message'] = 'Nro de documento ya existe'
           return res
        # if tipo_documento != 'ruc':
        #     res_partner = self.search([('vat', '=', nro_documento), ('active', '=', True)]).exists()
        #     if res_partner:
        #         res['message'] = 'Nro de documento ya existe'
        #         return res
        token = ''
        if self.company_id:
            tipo_busqueda = self.company_id.busqueda_ruc
            if tipo_busqueda == 'sinapi':
                return
            elif tipo_busqueda == 'apisperu':
                token = self.company_id.token_apisperu
            elif tipo_busqueda == 'apiperu':
                token = self.company_id.token_apiperu
        else:
            tipo_busqueda = self.env.company.busqueda_ruc
            if tipo_busqueda == 'sinapi':
                return
            elif tipo_busqueda == 'apisperu':
                token = self.env.company.token_apisperu
            elif tipo_busqueda == 'apiperu':
                token = self.env.company.token_apiperu
        try:
            if tipo_documento and nro_documento:
                try:
                    if tipo_busqueda == 'apisperu':
                        if tipo_documento  == 'dni':
                            if len(nro_documento) != 8:
                                return
                            return self.verify_dni_apisperu(token, nro_documento)
                        elif tipo_documento  == 'ruc':
                            if len(nro_documento) != 11:
                                return
                            return self.verify_ruc_apisperu(token, nro_documento)
                    elif tipo_busqueda == 'apiperu':
                        if tipo_documento  == 'dni':
                            if len(nro_documento) != 8:
                                return
                            return self.verify_dni_apiperu(token, nro_documento)
                        elif tipo_documento  == 'ruc':
                            if len(nro_documento) != 11:
                                return
                            return self.verify_ruc_apiperu(token, nro_documento)
                except Exception as ex:
                    _logger.error('Ha ocurrido un error {}'.format(ex))
        except Exception as e:
            res['message'] = 'Error en la conexion: '+str(self.company_id)
            return res
        return res

    @api.onchange('vat', 'l10n_latam_identification_type_id')
    def _onchange_identification(self):
        #_logger.info('***************variables: {0}'.format(tipo_docc))
        tipo_doc = self.l10n_latam_identification_type_id.name
        tipo_doc = tipo_doc.lower()
        #_logger.info('***************variables: {0}'.format(tipo_doc))
        if (tipo_doc == 'ruc' or tipo_doc == 'dni'):
            if(self.vat):
               # _logger.info('******************************entro a la busqueda')
                self.consulta_datos(tipo_doc, self.vat, format='json')
        else:
            #_logger.info('******************************retornado')
            return
        

    def verify_dni_apisperu(self, token, nro_documento):
        if not nro_documento:
            raise UserError("Debe seleccionar un DNI")
        url = QUERY_DOCUMENT_APISPERU['urls']['dni'].format(
            vat=nro_documento, token=token)
        result = requests.get(url, verify=False)
        if result.status_code == 200:
            result_json = result.json()
            if result_json['dni']:
                busqueda = {
                    'name': result_json['apellidoPaterno'].strip().upper() + ' ' + result_json['apellidoMaterno'].strip().upper() + ' ' + result_json['nombres'].strip().upper(),
                    'company_type': 'person',
                    'vat': nro_documento
                }
                self.update(busqueda)
                self.last_update = fields.Datetime.now()
                res = {'error': False, 'message': 'Ok', 'data': {'success': True, 'data': busqueda}}
                return res
            else:
                return {'error': True, 'message': 'Error, no se puede obtener datos de este DNI'}
        else:
            return {'error': True, 'message': 'Error al intentar obtener datos'}

    def verify_ruc_apisperu(self, token, nro_documento):
        district_obj = self.env['l10n_pe.res.city.district']
        url = QUERY_DOCUMENT_APISPERU['urls']['ruc'].format(
            vat=nro_documento, token=token)
        result = requests.get(url)
        if result.status_code == 200:
            result_json = result.json()
            if result_json['ruc']:
                ruc = result_json['ruc']
                if ruc[0:2] == '20':
                    district = district_obj.search([('name', '=ilike', result_json['distrito']),
                                                    ('city_id.name', '=ilike', result_json['provincia'])], limit=1)
                    if not district.exists():
                        district = district_obj.search(
                            [('code', '=', result_json['ubigeo'])])
                    busqueda = {
                        'name': result_json['razonSocial'],
                        'legal_name': result_json['razonSocial'],
                        'commercial_name': result_json['razonSocial'],
                        'street': result_json['direccion'].rsplit(' ', 3)[0],
                        'zip': result_json['ubigeo'],
                        'state_id': district.city_id.state_id.id,
                        'city_id': district.city_id.id,
                        'l10n_pe_district': district.id,
                        'state_sunat': result_json['estado'],
                        'condition_sunat': result_json['condicion'],
                        'company_type': 'company',
                        'vat': nro_documento
                    }
                    self.update(busqueda)
                    self.last_update = fields.Datetime.now()
                    res = {'error': False, 'message': 'Ok', 'data': {'success': True, 'data': busqueda}}
                    return res
                elif ruc[0:2] == '10':
                    busqueda = {
                        'name': result_json['razonSocial'],
                        'legal_name': result_json['razonSocial'],
                        'commercial_name': result_json['razonSocial'],
                        'state_sunat': result_json['estado'],
                        'condition_sunat': result_json['condicion'],
                        'company_type': 'person',
                        'vat': nro_documento                        
                    }
                    self.update(busqueda)
                    self.last_update = fields.Datetime.now()
                    res = {'error': False, 'message': 'Ok', 'data': {'success': True, 'data': busqueda}}
                    return res
            else:
                return {'error': True, 'message': 'Error, no se puede obtener datos de este DNI'}
        else:
            return {'error': True, 'message': 'Error al intentar obtener datos'}

    def verify_dni_apiperu(self, token, nro_documento):
        if not nro_documento:
            raise UserError("Debe seleccionar un DNI")
        endpoint = "https://apiperu.dev/api/dni/%s" % nro_documento
        headers = {
            "Authorization": "Bearer %s" % token,
            "Content-Type": "application/json",
        }
        result = requests.get(endpoint, data={}, headers=headers)
        if result.status_code == 200:
            result_json = result.json()
            if result_json['success'] == True:
                busqueda = {
                    'name': result_json['data']['nombre_completo'].strip(",").upper(),
                    'company_type': 'person',
                    'vat': nro_documento
                }
                self.update(busqueda)
                self.last_update = fields.Datetime.now()
                res = {'error': False, 'message': 'Ok', 'data': {'success': True, 'data': busqueda}}
                return res
            else:
                return {'error': True, 'message': 'Error, no se puede obtener datos de este DNI'}
        else:
            return {'error': True, 'message': 'Error al intentar obtener datos'}

    def verify_ruc_apiperu(self, token, nro_documento):
        district_obj = self.env['l10n_pe.res.city.district']
        endpoint = "https://apiperu.dev/api/ruc/%s" % nro_documento
        headers = {
            "Authorization": "Bearer %s" % token,
            "Content-Type": "application/json",
        }
        result = requests.get(endpoint, data={}, headers=headers)
        if result.status_code == 200:
            result_json = result.json()
            if result_json['success'] == True:
                ruc = result_json['data']['ruc']
                if ruc[0:2] == '20':
                    district = district_obj.search([('name', '=ilike', result_json['data']['distrito']),
                                                    ('city_id.name', '=ilike', result_json['data']['provincia'])], limit=1)
                    if not district.exists():
                        district = district_obj.search(
                            [('code', '=', result_json['data']['ubigeo'][2])])

                    busqueda = {
                        'name': result_json['data']['nombre_o_razon_social'],
                        'legal_name': result_json['data']['nombre_o_razon_social'],
                        'commercial_name': result_json['data']['nombre_o_razon_social'],
                        'street': result_json['data']['direccion'].split(',')[0],
                        'zip': result_json['data']['ubigeo'][2],
                        'state_id': district.city_id.state_id.id,
                        'city_id': district.city_id.id,
                        'l10n_pe_district': district.id,
                        'state_sunat': result_json['data']['estado'],
                        'condition_sunat': result_json['data']['condicion'],
                        'company_type': 'company',
                        'vat': nro_documento    
                    }
                    self.update(busqueda)
                    self.last_update = fields.Datetime.now()
                    res = {'error': False, 'message': 'Ok', 'data': {'success': True, 'data': busqueda}}
                    return res
                elif ruc[0:2] == '10':
                    busqueda = {
                        'name': result_json['data']['nombre_o_razon_social'],
                        'legal_name': result_json['data']['nombre_o_razon_social'],
                        'commercial_name': result_json['data']['nombre_o_razon_social'],
                        'state_sunat': result_json['data']['estado'],
                        'condition_sunat': result_json['data']['condicion'],
                        'company_type': 'person',
                        'vat': nro_documento
                    }
                    self.update(busqueda)
                    self.last_update = fields.Datetime.now()
                    res = {'error': False, 'message': 'Ok', 'data': {'success': True, 'data': busqueda}}
                    return res
            else:
                return {'error': True, 'message': 'Error, no se puede obtener datos de este RUC'}
        else:
            return {'error': True, 'message': 'Error al intentar obtener datos'}

    @api.constrains('vat')
    def _check_dni(self):
        if self.l10n_latam_identification_type_id.l10n_pe_vat_code == '1':
            try:
                int(self.vat)
                if len(self.vat) != 8:
                    msg2 = 'Error: DNI debe tener 8 digitos'
                    raise ValidationError(msg2)
                return
            except (TypeError, ValueError):
                msg = 'Error: DNI debe ser solo números'
                raise ValidationError(msg)

    # Buscamos la ubicacion de la compañia en la que nos encontramos
    # y la ponemos por defecto al guardar un contacto
    def _search_district(self):
        if self.env.context.get('company_id'):
            company = self.env['res.company'].browse(
                self.env.context['company_id'])
        else:
            company = self.env.company
        return company.partner_id.l10n_pe_district.id

    def _search_provincia(self):
        if self.env.context.get('company_id'):
            company = self.env['res.company'].browse(
                self.env.context['company_id'])
        else:
            company = self.env.company
        return company.partner_id.city_id.id

    def _search_company(self):
        if self.env.context.get('company_id'):
            company = self.env['res.company'].browse(
                self.env.context['company_id'])
        else:
            company = self.env.company
        return company.id

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for variables in vals_list:
    #         # Si el nro. de doc. ya existe
    #         if variables.get('company_type') == 'person':
    #             res_partner = self.search([('vat', '=', variables.get('vat')), ('active', '=', True)]).exists()
    #             if res_partner:
    #                 msg3 = 'Error: Contacto ya existe'
    #                 raise ValidationError(msg3)
    #         # if not variables.get('l10n_latam_identification_type_id'):
    #         #     raise ValidationError('Se necesita un Tipo de Documento, no debe estar vacío')
    #         if variables.get('l10n_latam_identification_type_id') == 4 or variables.get('l10n_latam_identification_type_id') == 5:
    #             vvat = variables.get('vat')
    #             if not vvat.isnumeric():
    #                 raise ValidationError('RUC/DNI deben ser solo números')
    #         company = self.env.company
    #         if not variables.get('l10n_pe_district') and not variables.get('city_id') and variables.get('state_id') == company.partner_id.state_id.id:
    #             variables['l10n_pe_district'] = self._search_district()
    #             variables['city_id'] = self._search_provincia()
    #     return super(ResPartner, self).create(vals_list)

    @api.model
    def create_from_ui(self, partner):
        # Si el nro. de doc. ya existe
        if partner.get('company_type') == 'person':
            res_partner = self.search([('vat', '=', partner.get('vat')), ('active', '=', True)]).exists()
            if res_partner:
                msg3 = 'Error: Contacto ya existe'
                raise ValidationError(msg3)
        # if not variables.get('l10n_latam_identification_type_id'):
        #     raise ValidationError('Se necesita un Tipo de Documento, no debe estar vacío')
        if partner.get('l10n_latam_identification_type_id') == 4 or partner.get('l10n_latam_identification_type_id') == 5:
            vvat = partner.get('vat')
            if not vvat.isnumeric():
                raise ValidationError('RUC/DNI deben ser solo números')
        company = self.env.company
        if not partner.get('l10n_pe_district') and not partner.get('city_id') and partner.get('state_id') == company.partner_id.state_id.id:
            partner['l10n_pe_district'] = self._search_district()
            partner['city_id'] = self._search_provincia()
        return super(ResPartner, self).create_from_ui(partner)
