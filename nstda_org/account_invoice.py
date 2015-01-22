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
    

    @api.multi
    def _get_analytic_lines(self):
        """ Method overwrite to allow multi-column analytic """
        
        company_currency = self.company_id.currency_id
        sign = 1 if self.type in ('out_invoice', 'in_refund') else -1

        iml = self.env['account.invoice.line'].move_line_get(self.id)
        for il in iml:
            il['analytic_lines'] = []
            if il['account_analytic_id']:
                if self.type in ('in_invoice', 'in_refund'):
                    ref = self.reference
                else:
                    ref = self.number
                if not self.journal_id.analytic_journal_id:
                    raise except_orm(_('No Analytic Journal!'),
                        _("You have to define an analytic journal on the '%s' journal!") % (self.journal_id.name,))
                currency = self.currency_id.with_context(date=self.date_invoice)
                il['analytic_lines'].append((0,0, {
                    'name': il['name'],
                    'date': self.date_invoice,
                    'account_id': il['account_analytic_id'],
                    'unit_amount': il['quantity'],
                    'amount': currency.compute(il['price'], company_currency) * sign,
                    'product_id': il['product_id'],
                    'product_uom_id': il['uos_id'],
                    'general_account_id': il['account_id'],
                    'journal_id': self.journal_id.analytic_journal_id.id,
                    'ref': ref,
                }))
                
            # Additional axis
            axises = [('business_area_id','business.area'),
                      ('sale_office_id','sale.office'),
                      ('profit_center_id','profit.center'),
                      ('wbs_project_id','wbs.project')]
            for axis in axises:
                if il.get(axis[0], False):
                    if self.type in ('in_invoice', 'in_refund'):
                        ref = self.reference
                    else:
                        ref = self.number
                    if not self.journal_id.analytic_journal_id:
                        raise except_orm(_('No Analytic Journal!'),
                            _("You have to define an analytic journal on the '%s' journal!") % (self.journal_id.name,))
                    currency = self.currency_id.with_context(date=self.date_invoice)
                    il['analytic_lines'].append((0,0, {
                        'name': il['name'],
                        'date': self.date_invoice,
                        'account_id': self.env[axis[1]].browse(il[axis[0]]).analytic_account_id.id,
                        'unit_amount': il['quantity'],
                        'amount': currency.compute(il['price'], company_currency) * sign,
                        'product_id': il['product_id'],
                        'product_uom_id': il['uos_id'],
                        'general_account_id': il['account_id'],
                        'journal_id': self.journal_id.analytic_journal_id.id,
                        'ref': ref,}))            
                
        return iml
    
    

class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'
    
    sale_office_id = fields.Many2one('sale.office', string='Sales Office')
    profit_center_id = fields.Many2one('profit.center', string='Profit Center')
    wbs_project_id = fields.Many2one('wbs.project', string='WBS/Project')


    @api.model
    def move_line_get_item(self, line):
        return {
            'type': 'src',
            'name': line.name.split('\n')[0][:64],
            'price_unit': line.price_unit,
            'quantity': line.quantity,
            'price': line.price_subtotal,
            'account_id': line.account_id.id,
            'product_id': line.product_id.id,
            'uos_id': line.uos_id.id,
            'account_analytic_id': line.account_analytic_id.id,
            'taxes': line.invoice_line_tax_id,
            # Org Dimension
            'business_area_id': line.invoice_id.business_area_id.id,
            'sale_office_id': line.sale_office_id.id,
            'profit_center_id': line.profit_center_id.id,
            'wbs_project_id': line.wbs_project_id.id,
        }
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
