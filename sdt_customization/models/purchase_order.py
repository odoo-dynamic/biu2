# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID
#from odoo.addons.product.models import decimal_precision as dp
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta
from lxml import etree

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.invoice_status=='no':
            partner_obj = self.env['res.partner'].search([('category_id.name', '=', 'Vendor')])
            partner_list=[]
            for line in partner_obj:
                partner_list.append(line.id)
            domain = {'partner_id': [('id', '=', partner_list)]}
            return {'domain': domain} 


    