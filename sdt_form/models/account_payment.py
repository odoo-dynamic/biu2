from odoo import models, fields, api, exceptions, _
from . import terbilang

class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"
   
    cash = fields.Boolean(string="Cash")
    chaque = fields.Boolean(string="Chaque / BG")
    bank_trans = fields.Boolean(string="Bank Transfer")
    say_acct_inv = fields.Char('Say', length=200)
    # display take home pay. terbilang
    @api.onchange('amount')
    def _onchange_net_salary(self):
        amount= self.amount
        cur= self.currency_id.name
        if self.currency_id.name == "USD":
            self.say_acct_inv = terbilang.terbilang(amount,cur,'en')
        elif self.currency_id.name == "IDR":
            self.say_acct_inv = terbilang.terbilang(amount,cur,'id')

    def terbilang_idr(self):
        return terbilang.terbilang(self.amount_total, 'idr', 'id')