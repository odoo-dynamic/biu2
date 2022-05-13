# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID
#from odoo.addons.product.models import decimal_precision as dp
from odoo.addons import decimal_precision as dp
from  odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import logging

_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    request_id = fields.Many2one('transfer.request', string='Transfer Request')

    @api.onchange('request_id')
    def onchange_request(self):
        if not self.request_id:
            return
        self.move_ids_without_package = self._getDetail()
        self.request_id=[]
    
    def _getDetail(self):
        hasil={}
        semua_hasil=[]
        for res in self.request_id.line_ids:
            qty_open=res.qty_request-res.qty_transfer
            if qty_open>0:
                sql_query="""select sum(quantity-reserved_quantity) as qty_available from stock_quant where product_id=%s and location_id=%s"""
                self.env.cr.execute(sql_query, (res.product_id.id,self.location_id.id,))
                qty_available = self.env.cr.fetchone()[0] or 0
            
                hasil=[0,0,{
                    'name':res.product_id.display_name,
                    'product_id':res.product_id.id,
                    'qty_available':qty_available,
                    'location_id': self.location_id.id,
                    'location_dest_id':self.location_dest_id.id,
                    'product_uom':res.product_uom_id.id,
                    'product_uom_qty':qty_open,
                    'request_line_id':res.id,
                    }]
                semua_hasil +=[hasil]
        return semua_hasil


    @api.onchange('picking_type_id')
    def onchange_picking_type(self):
        company_branch=self.picking_type_id.to_branch.id
        tr_obj=self.env['transfer.request'].search([('request_from','=',company_branch),('request_to','=',self.company_id.id),('state','in',('submit','partial'))])
        list_tr=[]
        for tr in tr_obj :
            list_tr.append(tr.id)
        domain = {'request_id': [('id', 'in', list_tr)]}
        return {'domain': domain}


    # def _action_done(self):
    #     res=super()._action_done()
        #return res
    def button_validate(self):
        if self.picking_type_id.is_receipt==True:
            simpan_avco = []
            for move in self.move_ids_without_package:
                # 1. simpan cost lama
                if move.price_unit==0:
                    standard_price = move.product_id.standard_price
                    qty_onhand = move.product_id.qty_available
                    # 2. update cost product menggunakan harga dari transfer
                    move.product_id.update({'standard_price': move.price_unit})
                    cost_average = ((qty_onhand * standard_price) + (move.quantity_done * move.price_unit)) / (qty_onhand + move.quantity_done)
                    #cost_average = round(cost_average, precision_digits)
                    simpan_avco.append([move.product_id.id, cost_average])
 
        res=super().button_validate()
        if self.picking_type_id.is_receipt==True:
            dct_avco = dict(simpan_avco)
            for move in self.move_ids_without_package:
                if move.price_unit==0:
                    # 3. update cost product menggunakan harga moving average baru
                    cost_average=dct_avco.get(move.product_id.id)
                    move.product_id.update({'standard_price': cost_average})

        if self.picking_type_id.is_branch==True:
            company_branch=self.picking_type_id.to_branch.id
            #opr_obj=self.env['stock.picking.type'].search([('id','=',self.picking_type_id.operation_type_branch)])
            sql_query = """
                    select a.default_location_src_id,a.default_location_dest_id,b.code from stock_picking_type a left join ir_sequence b on a.sequence_id=b.id where a.id=%s
                    """
            self.env.cr.execute(sql_query, (self.picking_type_id.operation_type_branch,))
            result = self.env.cr.dictfetchall()
            seq_code = 0
            default_location_dest_id = 0
            if result:
                for line in result:
                    seq_code = line['code']
                    default_location_dest_id = line['default_location_dest_id']
                    loc_id=line['default_location_src_id']
            
            #seq_code=opr_obj.sequence_id.code
            #name = self.env['ir.sequence'].next_by_code(seq_code)
            sql_query="""
                select a.id,a.date,a.reference,a.product_id,a.name,a.description_picking,a.product_uom_qty,a.product_uom,a.location_id,a.location_dest_id,
                c.account_id,c.credit,coalesce(c.credit/a.product_uom_qty,0) as price_unit,coalesce(a.request_line_id,0) as request_line_id 
                from stock_move a left join account_move b on a.id=b.stock_move_id left join account_move_line c on
                b.id=c.move_id and a.product_id=c.product_id and c.credit>0 where a.picking_id=%s;"""
            self.env.cr.execute(sql_query,(self.id,))
            result=self.env.cr.dictfetchall()
            list_sm=[]
            header_trans = {
                'scheduled_date': self.scheduled_date,
                'company_id': company_branch,
                'location_id': loc_id,
                'location_dest_id': default_location_dest_id,
                'picking_type_id': self.picking_type_id.operation_type_branch,
                'origin': self.name,
                'state':'assigned'}
            
            new_pick = self.env['stock.picking'].with_user(2).sudo().create(header_trans)
            picking_id=new_pick.id
            for line in result:  
                trans_dict={'name':line['name'],
                    'picking_id': picking_id,
                    'description_picking': line['description_picking'],
                    'product_id': line['product_id'],
                    'product_uom': line['product_uom'],
                    'company_id':company_branch,
                    'location_id': loc_id,
                    'location_dest_id': default_location_dest_id,
                    'product_uom_qty': line['product_uom_qty'],
                    'product_uom': line['product_uom'],
                    'price_unit': line['price_unit'],
                    'state':'assigned',
                    'picking_type_id': self.picking_type_id.operation_type_branch,
                    'origin': self.name}
                list_sml=[]
                new_move=self.env['stock.move'].with_user(2).sudo().create(trans_dict)
                move_id=new_move.id
                    
                #cek request and update
                if line['request_line_id']!=0:
                    sql_query="""select sum(qty_done) from stock_move_line where move_id=%s
                        """
                    self.env.cr.execute(sql_query,(line['id'],))
                    qty_done=self.env.cr.fetchone()[0] or 0
                    sql_query="""Update transfer_request_line set qty_transfer=qty_transfer+%s where id=%s;
                        Update transfer_request_line set qty_open=qty_request-qty_transfer where id=%s;
                        Update transfer_request_line set qty_open=0,state='close' where qty_open<=0 and id=%s;
                        """
                    self.env.cr.execute(sql_query,(qty_done,line['request_line_id'],line['request_line_id'],line['request_line_id'],))

                    #cek full or partial transfer
                    sql_query = """select request_id from transfer_request_line where id=%s
                            """
                    self.env.cr.execute(sql_query, (line['request_line_id'],))
                    request_id = self.env.cr.fetchone()[0] or 0
                    sql_query = """select count(1) from transfer_request_line where state='open' and request_id=%s
                            """
                    self.env.cr.execute(sql_query, (request_id,))
                    cek_open = self.env.cr.fetchone()[0] or 0
                    if cek_open==0:
                        sql_query="""Update transfer_request set state='transfer' where id=%s;"""
                    else:
                        sql_query="""Update transfer_request set state='partial' where id=%s;"""
                    self.env.cr.execute(sql_query,(request_id,))

                sql_query="""select a.date,a.product_id,a.product_uom_id,a.qty_done,a.lot_id,b.name as lot_name,a.reference,
                        a.location_id,a.location_dest_id,b.expiration_date,b.removal_date from stock_move_line a 
                        left join stock_production_lot b on a.lot_id=b.id
                        where a.move_id=%s
                        """
                self.env.cr.execute(sql_query,(line['id'],))
                res_sml=self.env.cr.dictfetchall()
                for sml in res_sml:
                    if sml['lot_id']:
                        lot_obj = self.env['stock.production.lot']
                        #carilot = lot_obj.with_user(2).sudo().search(['&',('name', '=', sml['lot_name']),('product_id','=',sml['product_id']),('company_id','=',company_branch)], limit=1)
                        sql_query="""select id,name,company_id,expiration_date,removal_date from stock_production_lot where name=%s and product_id=%s and company_id=%s limit 1
                        """
                        self.env.cr.execute(sql_query,(sml['lot_name'],sml['product_id'],company_branch,))
                        res_lot=self.env.cr.dictfetchall()

                        if res_lot:
                            for lot in res_lot:
                                lot_id = lot['id']
                                #exp_date=datetime.strptime(sml['expiration_date'], "%Y-%m-%d %H:%M:%S").datetime()
                                _logger.info('sdtlog : update lot_id %s exp date %s',lot_id,sml['expiration_date'])
                                carilot = lot_obj.with_user(2).sudo().search([('id', '=', lot_id)])
                                carilot.with_user(2).sudo().write({'expiration_date': sml['expiration_date'],
                                    'removal_date': sml['removal_date']})
                        else:
                            #exp_date=datetime.strptime(sml['expiration_date'], "%Y-%m-%d %H:%M:%S").datetime()
                            _logger.info('sdtlog : add exp date = %s',sml['expiration_date'])
                            lot_obj = self.env['stock.production.lot'].with_user(2).sudo().create(
                                {'name': sml['lot_name'], 
                                'product_id': sml['product_id'],
                                'expiration_date': sml['expiration_date'],
                                'removal_date': sml['removal_date'],
                                'company_id':company_branch }
                            )
                            lot_id = lot_obj.id
                        
                    else:
                        lot_id=[]
                    
                    move_line={'product_id': sml['product_id'],
                        'company_id': company_branch,
                        'move_id': move_id,
                        'picking_id': picking_id,
                        'lot_id': lot_id,
                        'product_uom_id': sml['product_uom_id'],
                        'qty_done': sml['qty_done'],
                        'location_id': loc_id,
                        'location_dest_id': default_location_dest_id,
                        'state':'assigned' }
                    new_move_line=self.env['stock.move.line'].with_user(2).sudo().create(move_line)
                    move_line_id=new_move_line.id

                    sml_obj=self.env['stock.move.line'].search([('id','=',move_line_id)])

            sql_query="""delete from stock_move_line a using stock_production_lot b where a.lot_id=b.id 
                    and b.company_id<>%s and a.picking_id=%s
                    """
            self.env.cr.execute(sql_query,(company_branch,picking_id,))

        return res    

# class StockMoveLine(models.Model):
#     _inherit = 'stock.move.line'

#     request_line_id = fields.Integer(string='Request Line',copy=False, default=0)


class StockMove(models.Model):
    _inherit = 'stock.move'

    request_line_id = fields.Integer(string='Request Line',copy=False, default=0)
    qty_available = fields.Float(string='Qty Available', track_visibility='onchange', digits=dp.get_precision('Product Unit of Measure'))
    