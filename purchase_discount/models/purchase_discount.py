from odoo import api, fields, models, _
from datetime import datetime


class SdtPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.price_total', 'order_line.price_subtotal')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })

class SdtPurchaseOrderLine(models.Model):
    _inherit ="purchase.order.line"

    price_befdisc = fields.Float('Price Before Discount')
    discount = fields.Float('Discount %')
    price_unit_tax = fields.Float('Real Unit Price', store=True)


    @api.depends('product_qty', 'price_unit', 'taxes_id', 'price_befdisc', 'discount')
    def _compute_amount(self):
        for line in self:
            if line.product_id.name!='Purchase Down Payment':
                line.price_unit = line.price_befdisc - (line.price_befdisc * line.discount)/100
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if line.price_subtotal and line.product_qty:
                line.price_unit_tax = line.price_subtotal / line.product_qty

    def _prepare_compute_all_values(self):
        res = super(SdtPurchaseOrderLine, self)._prepare_compute_all_values()
        if self.product_id.name!='Purchase Down Payment':
            res.update({'price_befdisc': self.price_befdisc,
                        'discount': self.discount})
        return res

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        if self.product_id.name!='Purchase Down Payment':
            res.update({'price_befdisc': self.price_befdisc,
                'discount_po':self.discount})
        return res