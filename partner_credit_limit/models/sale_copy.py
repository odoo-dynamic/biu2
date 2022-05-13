# See LICENSE file for full copyright and licensing details.


from odoo import _, api, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def check_limit(self):
        self.ensure_one()
        partner = self.partner_id
        user_id = self.env['res.users'].search([
            ('partner_id', '=', partner.id)], limit=1)
        if user_id and not user_id.has_group('base.group_portal') or not \
                user_id:
            moveline_obj = self.env['account.move.line']
            movelines = moveline_obj.search(
                [('partner_id', '=', partner.id),
                 ('account_id.user_type_id.name', 'in',
                    ['Receivable', 'Payable']),
                 ('parent_state','!=','cancel')]
            )
            confirm_sale_order = self.search(
                [('partner_id', '=', partner.id),
                 ('state', '=', 'sale'),
                 ('invoice_status', '!=', 'invoiced')])
            so_name = []
            move_id = []
            for rec in confirm_sale_order:
                so_name.append(rec.name)
            for data in movelines:
                move_id.append(data.move_id.id)
            
            move_obj = self.env['account.move'].search([('id', 'in', move_id),('invoice_origin', 'in', so_name)])
            id_move = []
            for id in move_obj:
                id_move.append(id.id)

            obj_movelines = []
            for lines in movelines:
                if lines.move_id.id in id_move:
                    obj_movelines.append(lines.id)

            debit, credit = 0.0, 0.0
            amount_total = 0.0
            for status in confirm_sale_order:
                amount_total += status.amount_total
            for line in movelines:
                if line.id not in obj_movelines:
                    credit += line.credit
                    debit += line.debit
                elif line.id in obj_movelines and line.credit != 0:
                    credit += line.credit
                    debit += line.debit
                    
            partner_credit_limit = (
                debit + amount_total) - credit
            available_credit_limit = round(
                partner.credit_limit - partner_credit_limit, 2)
            if partner_credit_limit > partner.credit_limit and \
                    partner.credit_limit > 0.0:
                if not partner.over_credit:
                    msg = 'Your available credit limit' \
                          ' Amount = %s \nCheck "%s" Accounts or Credit ' \
                          'Limits.' % (available_credit_limit,
                                       self.partner_id.name)
                    raise UserError(_('You can not confirm Sale '
                                      'Order. \n' + msg))
            return True

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.check_limit()
        return res

    @api.constrains('amount_total')
    def check_amount(self):
        for order in self:
            order.check_limit()

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res.partner_id.credit_limit > 0.0 and \
                not res.partner_id.over_credit:
            res.check_limit()
        return res
