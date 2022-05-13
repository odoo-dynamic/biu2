# -*- coding: utf-8 -*-
{
    'name': "SDT Form",

    'summary': """
        SDT Standard Form""",

    'description': """
        Standard Form all module by PT. Sinergi Data Totalindo
    """,

    'author': "Sinergi Data Totalindo, PT",
    'website': "http://www.sinergidata.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Report',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'account',
                'sale',
                'purchase',
                'web'
                ],

    # always loaded
    'data': [
        'report/sdt_standard_bill.xml',
        'report/sdt_standard_payment.xml',
        'report/sdt_standard_po.xml',
        'report/sdt_standard_invoice_alkes.xml',
        'report/sdt_standard_invoice_farmasi.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
