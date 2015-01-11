# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import itertools
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp


class sale_order(models.Model):
    _inherit = 'sale.order'
    
    order_type = fields.Selection([
            ('quotation','Quotation'),
            ('sale_order','Sales Order'),
        ], string='Order Type', readonly=True, index=True, 
        default=lambda self: self._context.get('order_type', 'sale_order'),)    
    quote_id = fields.Many2one('sale.order', string='Quotation Reference', readonly=True, index=True, ondelete='restrict')
    
    @api.one
    def action_button_convert_to_order(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        order = self.copy({'order_type': 'sale_order',
                           'quote_id': self.id})
        self.signal_workflow('convert_to_order')
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
