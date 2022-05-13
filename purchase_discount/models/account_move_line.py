# -*- coding: utf-8 -*-

from re import search

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    price_befdisc = fields.Float('Price Before Discount')
    discount_po = fields.Float('Discount')

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        res = super(AccountMove, self)._onchange_purchase_auto_complete()
        
        po = self.env['purchase.order'].search([('name', '=', self.invoice_origin)])
        for rec in po:
            line_po = self.env['purchase.order.line'].search([('order_id', '=', rec.id)])
            for line in self.invoice_line_ids:
                if line.product_id.id != 150:
                    id = str(line.id)
                    string = 'NewId_'
                    if search(string, id):
                        for data in line_po:
                            if line.product_id.id == data.product_id.id:
                                line.discount = data.discount
                                line.price_unit = data.price_befdisc
            
        return res