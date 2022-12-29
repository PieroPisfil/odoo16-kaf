# -*- coding: utf-8 -*-

{
    'name': "kaf-pos-base",
    'summary': "Configuraciones iniciales par el POS.",
    'version': '1.1',
    'description': """
       Configuraciones iniciales par el POS.
    """,
    'author': "Piero Pisfil",
    'depends': [
        'base',
        'contacts',
        'point_of_sale',
        'kaf-account-base',
    ],
    'data': [
        'views/res_config_settings_view.xml',
        'views/pos_order_view.xml',
        'views/pos_config_view.xml',
        # 'data/*',
    ],
    'assets': {
        'point_of_sale.assets': [
            'kaf-pos-base/static/js/Chrome.js',
            'kaf-pos-base/static/xml/Chrome.xml',
            'kaf-pos-base/static/lib/**/*',
            'kaf-pos-base/static/css/**/*',
            # 'kaf-pos-base/static/js/Screens/**/*',
            # 'kaf-pos-base/static/xml/**/*',
            # 'kaf-pos-base/static/xml/Screens/**/*',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
