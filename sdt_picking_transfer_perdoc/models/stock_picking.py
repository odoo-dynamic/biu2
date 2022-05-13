from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class SdtStockPicking(models.Model):
    _inherit="stock.picking"

    def button_validate(self):
        if self.picking_type_id.disallow_partial==True:
            for line in self.move_ids_without_package:
                if line.quantity_done<line.product_uom_qty:
                    raise UserError('Qty Done < Qty Demand, not allowed')

        res=super().button_validate()
        if self.id and self.state=='done':
            if self.location_dest_id.usage=='inventory':
                return res
            pick_obj=self.env['stock.picking'].search([('origin','=',self.name),('state','in',('draft','waiting','assigned'))], limit=1)
            if pick_obj:
                picking_id=pick_obj.id
                #cek stock.move
                for line in self.move_ids_without_package:
                    if line.state != 'cancel':
                        product_uom_qty=line.product_uom_qty
                        cek_mv=self.env['stock.move'].search([('product_id','=',line.product_id.id),('origin','=',self.name)])
                        if cek_mv:
                            sql_query="""Update stock_move set product_uom_qty=%s where product_id=%s and origin=%s;
                                """
                            self.env.cr.execute(sql_query,(product_uom_qty,line.product_id.id,line.reference,))
                        if not cek_mv:
                            # sql_query="""select picking_id,location_id,location_dest_id,origin,reference,state from stock_move 
                            #     where origin=%s limit 1;
                            #     """
                            # self.env.cr.execute(sql_query,(self.name,))
                            # result = self.env.cr.dictfetchall()
                            # for res in result:
                            #     picktarget_id=res['picking_id']
                            #     location_id=res['location_id']
                            #     location_dest_id=res['location_dest_id']
                            #     origin=res['origin']
                            #     reference=res['reference']
                            #     state=res['state']
                            sm_dict={'picking_id':pick_obj.id,
                                    'description_picking':line.description_picking,
                                    'location_id':pick_obj.location_id.id,
                                    'location_dest_id':pick_obj.location_dest_id.id,
                                    'product_id':line.product_id.id,
                                    'name':line.name,
                                    'product_uom':line.product_uom.id,
                                    'product_uom_qty':line.product_uom_qty,
                                    'origin':pick_obj.origin,
                                    'reference':pick_obj.name,
                                    'state':'assigned'
                                }
                            self.env['stock.move'].create(sm_dict)

                sql_query="""delete from stock_move_line where picking_id=%s;
                            """
                self.env.cr.execute(sql_query,(picking_id,))
                        
                #cek stock.move.line
                for field in self.move_line_ids:
                    sml_obj=self.env['stock.move.line'].search([('picking_id','=',picking_id),
                        ('reference','=',self.name),('product_id','=',field.product_id.id),
                        ('lot_id','=',field.lot_id.id)])
                    if sml_obj:
                        sql_query="""Update stock_move_line set product_qty=%s,product_uom_qty=%s where id=%s;
                            """
                        self.env.cr.execute(sql_query,(field.qty_done,field.qty_done,sml_obj.id,))
                        sql_query="""Update stock_quant set reserved_quantity=reserved_quantity+%s where product_id=%s and lot_id=%s and location_id=%s;
                            """
                        qty_update=field.qty_done-sml_obj.qty_done
                        self.env.cr.execute(sql_query,(qty_update,field.product_id.id,field.lot_id.id,move_obj.location_id.id,))
                    else:
                        move_obj=self.env['stock.move'].search([('picking_id','=',picking_id),
                        ('origin','=',self.name),('product_id','=',field.product_id.id)])
                        if move_obj:
                            sml_dict={'picking_id':picking_id,
                                'move_id':move_obj.id,
                                'location_id':move_obj.location_id.id,
                                'location_dest_id':move_obj.location_dest_id.id,
                                'product_id':move_obj.product_id.id,
                                'product_uom_id':move_obj.product_uom.id,
                                'lot_id':field.lot_id.id,
                                'product_uom_qty':field.qty_done,
                                'reference':move_obj.origin,
                                'state':'assigned'
                            }
                            self.env['stock.move.line'].create(sml_dict)
                            sql_query="""Update stock_quant set reserved_quantity=reserved_quantity+%s where product_id=%s and lot_id=%s and location_id=%s;
                                """
                            self.env.cr.execute(sql_query,(field.qty_done,field.product_id.id,field.lot_id.id,move_obj.location_id.id,))
                        else:
                            raise UserError('Stock Move not found..')
                            
        return res

    

    