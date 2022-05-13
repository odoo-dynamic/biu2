# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID
#from odoo.addons.product.models import decimal_precision as dp
from odoo.addons import decimal_precision as dp
from  odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_STATES = [
    ('open', 'Draft'),
    ('submit', 'Submitted'),
    ('partial', 'Partial Transfer'),
    ('transfer', 'Transfered')
]


class TransferRequest(models.Model):
    _name = 'transfer.request'
    _description = 'Transfer Request'
    _inherit = ['mail.thread']


    @api.model
    def _get_default_company(self):
        return self.env.company.id

    name = fields.Char('Name', size=32, track_visibility='onchange',copy=True,index=True)
    date_request = fields.Date('Issued Date', default=fields.Date.context_today, track_visibility='onchange')
    request_from = fields.Many2one('res.company', string='Request From',default=_get_default_company)
    request_to = fields.Many2one('res.company', string='Request To')
    description = fields.Text('Description')
    line_ids = fields.One2many('transfer.request.line', 'request_id','Products to Issued',copy=True,track_visibility='onchange')
    state = fields.Selection(selection=_STATES,string='Status',index=True,track_visibility='onchange',required=True,copy=False,default='open')

    def _get_default_name(self):
        name=self.env['ir.sequence'].next_by_code('transfer.request')
        return name

    def unlink(self):
        if self.state!='open':
            raise UserError('Hanya status draft yang bisa di hapus')
        return super().unlink()

    def submit(self):
        if not self.line_ids:
            raise UserError(('Line Detail is not found..'))
        self.name=self._get_default_name()
        self.state='submit'


class TransferRequestLine(models.Model):
    _name = "transfer.request.line"
    _description = "Transfer Request Line"
    _inherit = ['mail.thread']

    request_id = fields.Many2one('transfer.request','Transfer Request',ondelete='cascade', readonly=True)
    name = fields.Char('Description')
    product_id = fields.Many2one('product.product', 'Product',track_visibility='onchange')
    product_uom_id = fields.Many2one(comodel_name='uom.uom', inverse_name='id', string='UoM', store=True)
    qty_onhand = fields.Float(string='Qty Onhand', track_visibility='onchange', digits=dp.get_precision('Product Unit of Measure'))
    qty_request = fields.Float(string='Qty Request', track_visibility='onchange', digits=dp.get_precision('Product Unit of Measure'))
    qty_transfer = fields.Float(string='Qty Transfer', track_visibility='onchange',default=0,copy=False, digits=dp.get_precision('Product Unit of Measure'))
    qty_open = fields.Float(string='Qty Open', track_visibility='onchange', digits=dp.get_precision('Product Unit of Measure'))
    state = fields.Selection(selection=_STATES,string='Status',track_visibility='onchange',copy=False,default='open')


    @api.onchange('product_id')
    def onchange_product(self):
        if not self.product_id:
            return
        uom_id=self.product_id.uom_id.id
        self.product_uom_id=uom_id
        
        loc_id=self.request_id.request_from.location_onhand
        company_id=self.request_id.request_from.id        
        self.qty_onhand=self._getonhand(loc_id,self.product_id.id,company_id)


    def _getonhand(self,loc_id,product_id,company_id):
        if not loc_id:
            raise UserError('Location Onhand harus disetting terlebih dahulu di module company')
        sql_query="""select sum(a.quantity) from stock_quant a inner join res_company_stock_location_rel b on a.location_id= b.stock_location_id 
                and a.company_id=b.res_company_id
                where a.product_id=%s and a.company_id=%s
                """
        self.env.cr.execute(sql_query,(product_id,company_id,))
        res=self.env.cr.fetchone()[0] or 0
        return res
                

class ResCompany(models.Model):
    _inherit = "res.company"

    location_onhand = fields.Many2one('stock.location', 'Location OnHand',track_visibility='onchange')