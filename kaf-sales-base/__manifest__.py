# -*- coding: utf-8 -*-

{
    'name': "kaf-sales-base",
    'summary': "Configuraciones iniciales para las ventas",
    'version': '1.1',
    'description': """
       Configuraciones iniciales en las ventas para la facturacion con SUNAT y algunos reportes para inventario.
    """,
    'author': "Piero Pisfil",
    'depends': [
        'stock',
        'contacts',
        'kaf-ticket-base',
        'sale',
        'kaf-contacts-base',
        'web',
    ],
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'data/report_layout.xml',
        'report/stock_report_ticket_views.xml',
        'views/sale_make_invoice_advance_views.xml',
    ],
    # 'assets': {
    #     'point_of_sale.assets': [
    #         'kaf-whatsapp-pos/static/src/js/*',
    #         'kaf-whatsapp-pos/static/src/css/**/*',
    #         'kaf-whatsapp-pos/static/src/js/Screens/**/*',
    #     ],
    #     'web.assets_qweb': [
    #         'kaf-whatsapp-pos/static/src/xml/**',
    #         'kaf-whatsapp-pos/static/src/xml/Screens/**/*',
    #     ],
    # },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
