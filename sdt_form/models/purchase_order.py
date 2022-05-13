from odoo import models, fields, api, exceptions,_
from . import terbilang


class TerbilangPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    say_acct_inv = fields.Char('Say', length=200,compute="terbilang_idr")
    # display take home pay. terbilang
    @api.depends('amount_total')
    def terbilang_idr(self):
        amount= self.amount_total
        cur= self.currency_id.name
        if self.currency_id.name == "USD":
            self.say_acct_inv = terbilang.terbilang(amount,cur,'en')
        elif self.currency_id.name == "IDR":
            self.say_acct_inv = terbilang.terbilang(amount,cur,'id')
            

    # @api.multi
    # def _prepare_invoice(self):
    #     res = super(Acct, self)._prepare_invoice()
    #     res.update({'say_acct_inv2': self.say_acct_inv})
    #     return res