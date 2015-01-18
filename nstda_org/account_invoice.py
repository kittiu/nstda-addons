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



class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    business_area_id = fields.Many2one('business.area',
        string='Business Area', readonly=True, states={'draft': [('readonly', False)]},)

class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'
    
    sale_office_id = fields.Many2one('sale.office', string='Sales Office')
    profit_center_id = fields.Many2one('profit.center', string='Profit Center')
    wbs_project_id = fields.Many2one('wbs.project', string='WBS/Project')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
