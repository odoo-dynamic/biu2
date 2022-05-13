# -*- coding: utf-8 -*-

from odoo import api, fields, models, _ , SUPERUSER_ID
#from odoo.addons.product.models import decimal_precision as dp
from odoo.addons import decimal_precision as dp
from  odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ResCompany(models.Model):
    _inherit = "res.company"

    location_onhand = fields.Many2many(comodel_name='stock.location', string='Location OnHand', track_visibility='onchange')

    # @api.onchange('id')
    # def onchange_id(self):
    #     loc_obj=self.env['stock.location'].search([('company_id','=',self.id)])
    #     list_loc=[]
    #     for loc in loc_obj :
    #         list_loc.append(loc.id)
    #     domain = {'location_onhand': [('id', 'in', list_loc)]}
    #     return {'domain': domain}
    