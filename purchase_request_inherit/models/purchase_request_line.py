# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    @api.onchange('product_id','product_qty')
    def onchange_product(self):
        if self.product_id:
            self.product_uom_id=self.product_id.uom_po_id.id

