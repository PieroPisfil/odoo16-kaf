# -*- coding: utf-8 -*-

# libreria para los mensaje para consola
import logging

from odoo import fields, models, api
# librería para mensajes
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

copier_formats = [('no_tiene', 'No tiene'),
                  ('a4', 'Hasta A4'),
                  ('letter', 'Hasta A4 - Letter(Carta)'),
                  ('legal', 'Hasta A4 - Legal(Oficio)'),
                  ('a3', 'Hasta A3'), ]


class Datasheet(models.Model):
    _name = "datasheet"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']

    name = fields.Char(string='Nombre de Modelo')
    fotocopiers_ids=fields.One2many('product.template','modelo_fotocopiadora_id')
    copy_brand = fields.Many2one(
        comodel_name='copier.brand',
        string='Marca')
    tipo_funcion = fields.Selection(selection=[
        ('multifuncional-laser',
         'Copiadora Multifuncional Laser (Impresora-Copiadora-Escaner-Fax)'),
        ('only-printer-laser', 'Impresora Laser'),
    ], string='Tipo', default='multifuncional-laser')
    tipo_color = fields.Selection(selection=[
        ('monocroma', 'Monócroma'),
        ('color', 'Color'),
    ], string='Tipo')
    mns_tipo_color = fields.Char(string='Descripcion Tipo Color')

    paper_format_luna = fields.Selection(
        copier_formats, string='Formato Luna')
    paper_format_bandeja = fields.Selection(
        copier_formats, string='Formato Bandeja')
    paper_format_bypass = fields.Selection(
        copier_formats, string='Formato Bypass')
    paper_format_adf = fields.Selection(
        copier_formats, string='Formato ADF')

    copy_speed = fields.Integer(string='Velocidad de copiado')  # ppm

    printer_speed = fields.Integer(string='Velocidad de impresión')  # ppm
    printer_max_resolution = fields.Integer(
        string='Resolución máxima de impresión')  # dpi

    scan_max_speed_byn = fields.Integer(
        string='Velocidad máxima de escaner en ByN')  # ppm
    scan_max_speed_color = fields.Integer(
        string='Velocidad máxima de escaner en color')  # ppm
    scan_max_resolution = fields.Integer(
        string='Resolución máxima de escaner en ByN')  # dpi
    scan_duplex_scan = fields.Selection([
        ('twoscan', 'Two-scan'),
        ('duplex', 'Duplex'),
    ], string='Tipo de scaner duplex')

    product_realted_id = fields.Many2one(
        comodel_name='product.template',
        string='Fotocopiadora en el inventario'
    )
    product_toner_compatible = fields.Many2many(
        comodel_name='product.template',
        string='Toner Compatibles'
    )

    link_brochure = fields.Char(string='Link a Brochure')
    tiene_brochure = fields.Boolean(string='Tiene brochure')
    brochure_file = fields.Binary(string='Brochure')
    brochure_filename = fields.Char()

    porcentaje = fields.Integer(
        related="porcentaje_value", string='Porcentaje')
    porcentaje_value = fields.Integer(string='Porcentaje valor')

    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('aprobado', 'Aprobado'),
        ('cancelado', 'Cancelado'),
    ], default='borrador', string='Estados', copy=False)
    fch_aprobado = fields.Datetime(string='Fecha aprobado', copy=False)

    active = fields.Boolean(default=True)

    def aprobar_datasheet(self):
        logger.info('***************Entró a la función aprobar datasheet')
        self.state = 'aprobado'
        self.fch_aprobado = fields.Datetime.now()

    def cancelar_datasheet(self):
        self.state = 'cancelado'

    # funcion para borrar registros :O
    def unlink(self):
        logger.info('***************Entró a la función unlink')
        if self.state == 'aprobado':
            raise UserError(
                'No se puede eliminar el registro, debe estar en cancelado o borrador.')
            # se hace un break y no se ejecuta lo siguiente
        # Llamado a la funcion original de borrado
        super(Datasheet, self).unlink()

    @api.model
    def create(self, variables):
        logger.info('***************variables: {0}'.format(variables))
        # Llamado a la funcion original de creación
        return super(Datasheet, self).create(variables)

    def write(self, variables):
        logger.info('***************variables: {0}'.format(variables))
        if 'tipo_funcion' in variables:
            raise UserError('El tipo funcion no se puede cambiar')
        # Llamado a la funcion original de editar registros
        return super(Datasheet, self).write(variables)

    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = self.name + '(Copia)'
        default['porcentaje_value'] = 10
        # Llamado a la funcion original de duplicar registros
        return super(Datasheet, self).copy(default)

    @api.onchange('tipo_color')
    def _onchange_tipo_color(self):
        if self.tipo_color:
            if self.tipo_color == 'monocroma':
                self.mns_tipo_color = 'La copiadora es monócroma'
            if self.tipo_color == 'color':
                self.mns_tipo_color = 'La copiadora es de color'
        else:
            self.mns_tipo_color = False
