# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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

from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime

class sale_create_billing_plan(models.TransientModel):
    _name = 'sale.create.billing.plan'
    _description = 'Create Billing Plan'

    num_installment = fields.Integer('Number of Installment', default=1)
    installment_ids = fields.One2many('sale.create.billing.plan.installment', 'plan_id', string='Installments')

    @api.one
    def do_create_billing_plan(self):
        order = self.env['sale.order'].browse(self._context['active_id'])
        order.billing_plan_ids.unlink()
        lines = []
        for order_line in order.order_line:
            first_install = True
            for install in self.installment_ids:
                lines.append({
                    'order_id': order.id,
                    'order_line_id': order_line.id,
                    'installment': install.installment,
                    'date_invoice': install.date_invoice,
                    'bill_percent': first_install and 100.0 or 0.0,
                    'bill_amount': first_install and order_line.price_subtotal or 0.0
                })
                first_install = False
        order.billing_plan_ids = lines

    @api.onchange('num_installment')
    def _onchange_price(self):
        i, lines = 0, []
        while i < self.num_installment:
            i+=1
            lines.append({'installment': i})
        self.installment_ids = lines   
    
class sale_create_billing_plan_installment(models.TransientModel):
    _name = 'sale.create.billing.plan.installment'
    _description = 'Create Billing Plan Installments'

    plan_id = fields.Many2one('sale.create.billing.plan', string='Wizard Reference', readonly=True)  
    installment = fields.Integer(string='Installment', readonly=True, help="Group of installment. Each group will be an invoice")
    date_invoice = fields.Date(string='Invoice Date', required=True, help="Invoice created for this installment will be using this date")
    