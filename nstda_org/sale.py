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
from openerp.osv import fields, osv

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp


class sale_order(models.Model):
    _inherit = 'sale.order'

    # Org Structure
    business_area_id = fields.Many2one('business.area', string='Business Area', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        track_visibility='always')

    @api.model
    def _prepare_invoice(self, order, lines):
        res = super(sale_order, self)._prepare_invoice(order, lines)
        res.update({
            'business_area_id': order.business_area_id and order.business_area_id.id or False,
        })
        return res

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    sale_office_id = fields.Many2one('sale.office',
        string='Sales Office', readonly=True, states={'draft': [('readonly', False)]},)
    profit_center_id = fields.Many2one('profit.center',
        string='Profit Center', readonly=True, states={'draft': [('readonly', False)]},)
    wbs_project_id = fields.Many2one('wbs.project',
        string='WBS/Project', readonly=True, states={'draft': [('readonly', False)]},)

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(line, account_id=account_id)
        res.update({
            'sale_office_id': line.sale_office_id and line.sale_office_id.id or False,
            'profit_center_id': line.profit_center_id and line.wbs_project_id.id or False,
            'wbs_project_id': line.wbs_project_id and line.wbs_project_id.id or False,
        })
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
