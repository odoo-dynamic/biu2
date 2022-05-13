# -*- encoding: utf-8 -*-

{
    'name': 'Picking Transfer per Document',
    'version': '1.0',
    'category': 'Inventory',
    'author':'Sinergi Data Totalindo, PT',
    'description': """A Picking Transfer per Document is an instruction to create picking in target operation  
        with certain document transfer, so that they are available at a certain point in target operation type.
    """,
    'summary': 'Create Picking Transfer per document',
    'website': 'http://sinergidata.co.id',
    'data': [
        'views/stock_picking_type.xml',
    ],
    'depends': ['stock'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 105,
    'license': 'AGPL-3',
}
