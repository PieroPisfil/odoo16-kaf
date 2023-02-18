# -*- coding: utf-8 -*-

{
    'name': "kaf-fotocopiadoras-datacopier",
    'summary': "Modulo personalizado para agregar modelos de fotocopiadoras en Odoo",
    'version': '1.1',
    'description': """
       Fotocopier's data
    """,
    'author': "Piero Pisfil",
    'depends': [
        'product',
        'stock',
        'mail',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/copier_brand.xml',
        'report/reporte_datasheet.xml',
        'views/menu.xml',
        'views/datasheet_view.xml',
        'views/copier_brand_view.xml',
        'views/product_template_view.xml',
        'views/archivo_venta_view.xml'
    ],
    'license': 'LGPL-3',
}
