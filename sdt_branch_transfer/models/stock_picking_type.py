# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID
#from odoo.addons.product.models import decimal_precision as dp
from odoo.addons import decimal_precision as dp
from  odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_branch = fields.Boolean(string='Transfer Branch')
    to_branch = fields.Many2one('res.company', string='To Branch')
    operation_type_branch = fields.Integer(string="Operation Type Branch")
    is_receipt = fields.Boolean(string='Transfer Receipt')
