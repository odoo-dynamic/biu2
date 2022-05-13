# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID
#from odoo.addons.product.models import decimal_precision as dp
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta
from lxml import etree

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('move_type')
    def onchange_movetype(self):
        if self.move_type=='in_invoice':
            partner_obj = self.env['res.partner'].search([('category_id.name', '=', 'Vendor')])
            partner_list=[]
            for line in partner_obj:
                partner_list.append(line.id)
            domain = {'partner_id': [('id', '=', partner_list)]}
            return {'domain': domain} 
        elif self.move_type=='in_refund':
            partner_obj = self.env['res.partner'].search([('category_id.name', '=', 'Vendor')])
            partner_list=[]
            for line in partner_obj:
                partner_list.append(line.id)
            domain = {'partner_id': [('id', '=', partner_list)]}
            return {'domain': domain}
        elif self.move_type=='in_receipt':
            partner_obj = self.env['res.partner'].search([('category_id.name', '=', 'Vendor')])
            partner_list=[]
            for line in partner_obj:
                partner_list.append(line.id)
            domain = {'partner_id': [('id', '=', partner_list)]}
            return {'domain': domain}
        elif self.move_type=='out_invoice':
            partner_obj = self.env['res.partner'].search([('category_id.name', '=', 'Customer')])
            partner_list=[]
            for line in partner_obj:
                partner_list.append(line.id)
            domain = {'partner_id': [('id', '=', partner_list)]}
            return {'domain': domain}  
        elif self.move_type=='out_refund':
            partner_obj = self.env['res.partner'].search([('category_id.name', '=', 'Customer')])
            partner_list=[]
            for line in partner_obj:
                partner_list.append(line.id)
            domain = {'partner_id': [('id', '=', partner_list)]}
            return {'domain': domain}  

#     @api.model
#     def _fields_view_get(self, view_id=None, view_type='form',toolbar=False, submenu=False):
#         res =super(AccountMove,self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
#         if view_type=='form':
#             doc = etree.XML(res['arch'])
#             nodes=doc.xpath("//field[@name='partner_id']")
#             types=doc.xpath("//field[@name='move_type']")
#             if nodes:
#                 for node in nodes:
#                     node.set('domain', "[('category_id.name', '=', 'Customer')]")
#                     #node.set('widget', '')
#             res['arch']=etree.tostring(doc,encoding='unicode')

#    return res


    