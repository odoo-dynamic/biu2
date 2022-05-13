from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class SdtStockPickingType(models.Model):
    _inherit="stock.picking.type"

    disallow_partial = fields.Boolean('Disallow Partial')
    

