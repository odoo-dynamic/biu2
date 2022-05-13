# -*- encoding: utf-8 -*-

{
    'name': 'SDT Purchase Discount',
    'version': '1.0',
    'category': 'Accounting',
    'author':'Sinergi Data Totalindo, PT',
    'description': """
    Discount in purchse order
    """,
    'summary': 'Discount Purchase',
    'website': 'http://sinergidata.co.id',
    'data': [
        'views/purchase_discount_view.xml',
        'views/invoice_discount_view.xml',
    ],
    'depends': ['base', 'purchase', 'account'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 105,
    'license': 'AGPL-3',
}
