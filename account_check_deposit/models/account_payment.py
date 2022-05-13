from odoo import _, api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.exceptions import ValidationError, UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    check_deposit = fields.Boolean(string='Check Deposit', default=False)
    deposit_due = fields.Date(string='Deposit Due')
    deposit_no = fields.Char(string='Deposit No',size=50)

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        for line in self:
            if line.check_deposit==True:
                if line.deposit_no==False:
                    raise UserError(('Deposit Number can not be empty'))
            move_line_obj=self.env['account.move.line'].search([('payment_id','=',line.id)])
            if move_line_obj:
                if line.deposit_due:
                    move_line_obj.write({'deposit_no':line.deposit_no,'deposit_due':line.deposit_due,'name':line.deposit_due})
        return res


class AccountRegisterPayment(models.TransientModel):
    _inherit = "account.payment.register"

    check_deposit = fields.Boolean(string='Check Deposit', default=False)
    deposit_due = fields.Date(string='Deposit Due')
    deposit_no = fields.Char(string='Deposit No',size=50)

    def _create_payment_vals_from_wizard(self):
        res = super(AccountRegisterPayment, self)._create_payment_vals_from_wizard()
        if self.check_deposit==True:
            if res['ref']:
                res['ref']=self.deposit_no + ' - ' + res['ref']
            else:
                res['ref']=self.deposit_no 
            res['check_deposit'] = self.check_deposit
            res['deposit_no'] = self.deposit_no
            res['deposit_due'] = self.deposit_due
        return res

    def _create_payment_vals_from_batch(self,batch_result):
        res = super(AccountRegisterPayment, self)._create_payment_vals_from_batch(batch_result)
        if self.check_deposit==True:
            if res['ref']:
                res['ref']=self.deposit_no + ' - ' + res['ref']
            else:
                res['ref']=self.deposit_no 
            res['check_deposit'] = self.check_deposit
            res['deposit_no'] = self.deposit_no
            res['deposit_due'] = self.deposit_due
        return res
    
    # def _prepare_payment_vals(self, invoices):
    #     res = super(AccountRegisterPayment, self)._prepare_payment_vals(invoices)
    #     res['check_deposit'] = self.check_deposit
    #     res['deposit_no'] = self.deposit_no
    #     res['deposit_due'] = self.deposit_due
    #     return res

    def action_create_payments(self):
        if self.check_deposit == True:
            if self.deposit_no == False:
                raise UserError(('Deposit Number can not be empty'))
        res = super(AccountRegisterPayment, self).action_create_payments()
        return res