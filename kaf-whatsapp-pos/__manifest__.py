# -*- coding: utf-8 -*-

{
    'name': "kaf-whatsapp-pos",
    'summary': "Envía comprobantes por whatsapp desde el pos, previa configuración.",
    'version': '1.1',
    'description': """
       Los comprobantes los envía por whatsapp
    """,
    'author': "Piero Pisfil",
    'depends': [
        'base',
        'contacts',
        'point_of_sale',
        'kaf-pos-base',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/menu.xml',
        'views/whatsapp_instancia_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'kaf-whatsapp-pos/static/src/js/*',
            'kaf-whatsapp-pos/static/src/css/**/*',
            'kaf-whatsapp-pos/static/src/js/Screens/**/*',
            'kaf-whatsapp-pos/static/src/xml/**',
            'kaf-whatsapp-pos/static/src/xml/Screens/**/*',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
