# -*- coding: utf-8 -*-

from re import search

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        res = super(AccountMove, self)._onchange_purchase_auto_complete()
        
        po = self.env['purchase.order'].search([('name', '=', self.invoice_origin)])
        for rec in po:
            line_po = self.env['purchase.order.line'].search([('order_id', '=', rec.id)])
            for line in self.invoice_line_ids:
                if 'Down Payment' not in line.product_id.name:
                    id = str(line.id)
                    string = 'NewId_'
                    if not search(string, id):
                        for data in line_po:
                            if line.product_id.id == data.product_id.id:
                                line.write({'discount': data.discount, 'price_unit': data.price_befdisc})
            
        return res
    
    # def action_post(self):
    #     res = super(AccountMove, self).action_post()
    #     for rec in self:
    #         for move in rec.invoice_line_ids:
    #             if move.product_id.id == 1:
    #                 if move.purchase_line_id:
    #                     move.price_unit = move.purchase_line_id.price_unit
    #     return res