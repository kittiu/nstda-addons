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
    
    use_billing_plan = fields.Boolean(string='Use Billing Plan', readonly=True, states={'draft': [('readonly', False)]}, 
        default=False, help="It indicates that the invoice has been sent.")
    billing_plan_ids = fields.One2many('sale.billing.plan', 'order_id', string='Billing Plan',
        readonly=True, states={'draft': [('readonly', False)]})
                
    @api.onchange('use_billing_plan')
    def _onchange_use_billing_plan(self):
        if self.use_billing_plan:
            self.order_policy = 'manual'
        else:
            default_order_policy = self.env['ir.values'].get_default('sale.order', 'order_policy')
            self.order_policy = default_order_policy or 'manual'
            
    @api.model
    def _check_billing_plan(self):
        if self.use_billing_plan:
            for order_line in self.order_line:
                bill_lines = self.env['sale.billing.plan'].search([('order_line_id','=',order_line.id)])
                total_percent = sum([line.bill_percent for line in bill_lines])
                total_amount = sum([line.bill_amount for line in bill_lines])
                if total_percent != 100:
                    raise except_orm(_('Plan Amount Mismatch!'),
                            _("'%s', plan amount %d not equal to line amount %d!") 
                            % (order_line.product_id.name, total_amount, order_line.price_subtotal))
        return True
    
    @api.multi
    def action_invoice_create(self, grouped=False, states=None, date_invoice = False):
        # Mixed billing plan and grouping is not allowed.
        if grouped and (True in [order.use_billing_plan for order in self]):
            raise except_orm(_('Warning'),
                    _("Mixing normal SO and SO with Billing Plan not allowed!"))
        # Case use_billing_plan, create multiple invoice by installment
        if self[0].use_billing_plan:
            plan_obj = self.env['sale.billing.plan']
            for order in self:
                installments = list(set([plan.installment for plan in order.billing_plan_ids]))
                for installment in installments:
                    # Getting billing plan for each installment
                    blines = plan_obj.search([('installment', '=', installment), ('order_id', '=', order.id)])
                    dict = {}
                    for b in blines:
                        dict.update({b.order_line_id: b.bill_percent}) 
                    order = order.with_context(bill_plan_percent=dict) 
                    res = order.action_invoice_create_rev(grouped=grouped, states=states, date_invoice=date_invoice)
        else:
            res = self.action_invoice_create_rev(grouped=grouped, states=states, date_invoice=date_invoice)
        return res

    # *** THIS IS AN OVERWRITE METHOD, marked as 'kittiu' ***
    # Overwrite just to pass context into "obj_sale_order_line.invoice_line_create"
    # Then rename this to _rev, so that we can have our own action_invoice_create.
    # Note that similar thing is done in create_invoice_line_percentage, if it is to be used, make sure to merge.
    def action_invoice_create_rev(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        if states is None:
            states = ['confirmed', 'done', 'exception']
        res = False
        invoices = {}
        invoice_ids = []
        invoice = self.pool.get('account.invoice')
        obj_sale_order_line = self.pool.get('sale.order.line')
        partner_currency = {}
        # If date was specified, use it as date invoiced, usefull when invoices are generated this month and put the
        # last day of the last month as invoice date
        if date_invoice:
            context = dict(context or {}, date_invoice=date_invoice)
        for o in self.browse(cr, uid, ids, context=context):
            currency_id = o.pricelist_id.currency_id.id
            if (o.partner_id.id in partner_currency) and (partner_currency[o.partner_id.id] <> currency_id):
                raise osv.except_osv(
                    _('Error!'),
                    _('You cannot group sales having different currencies for the same partner.'))

            partner_currency[o.partner_id.id] = currency_id
            lines = []
            for line in o.order_line:
                if line.invoiced:
                    continue
                elif (line.state in states):
                    lines.append(line.id)
            # kittiu: after looking around for solution, the only way is 
            # created_lines = obj_sale_order_line.invoice_line_create(cr, uid, lines)
            created_lines = obj_sale_order_line.invoice_line_create(cr, uid, lines, context=context)
            # --
            if created_lines:
                invoices.setdefault(o.partner_invoice_id.id or o.partner_id.id, []).append((o, created_lines))
        if not invoices:
            for o in self.browse(cr, uid, ids, context=context):
                for i in o.invoice_ids:
                    if i.state == 'draft':
                        return i.id
        for val in invoices.values():
            if grouped:
                res = self._make_invoice(cr, uid, val[0][0], reduce(lambda x, y: x + y, [l for o, l in val], []), context=context)
                invoice_ref = ''
                origin_ref = ''
                for o, l in val:
                    invoice_ref += (o.client_order_ref or o.name) + '|'
                    origin_ref += (o.origin or o.name) + '|'
                    self.write(cr, uid, [o.id], {'state': 'progress'})
                    cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (o.id, res))
                    self.invalidate_cache(cr, uid, ['invoice_ids'], [o.id], context=context)
                #remove last '|' in invoice_ref
                if len(invoice_ref) >= 1:
                    invoice_ref = invoice_ref[:-1]
                if len(origin_ref) >= 1:
                    origin_ref = origin_ref[:-1]
                invoice.write(cr, uid, [res], {'origin': origin_ref, 'name': invoice_ref})
            else:
                for order, il in val:
                    res = self._make_invoice(cr, uid, order, il, context=context)
                    invoice_ids.append(res)
                    self.write(cr, uid, [order.id], {'state': 'progress'})
                    cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order.id, res))
                    self.invalidate_cache(cr, uid, ['invoice_ids'], [order.id], context=context)
        return res    

    @api.multi
    def manual_invoice(self, context=None):
        # If use_billing_plan, view invoices in list view.
        res = super(sale_order, self).manual_invoice()
        if self[0].use_billing_plan:
            res = self.action_view_invoice()
        return res

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        res = super(sale_order_line, self)._prepare_order_line_invoice_line(line, account_id=account_id)
        line_percent = self._context.get('bill_plan_percent', False)
        if line_percent:
            res.update({'quantity': (res.get('quantity') or 0.0) * (line and line_percent[line] or 0.0) / 100})
        return res

    # A complete overwrite method of sale_order_line
    # This is the same fix as in create_invoice_line_percentage, if this addon depend on it, this can be removed.
    def _fnct_line_invoiced(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, False)
        uom_obj = self.pool.get('product.uom')
        for this in self.browse(cr, uid, ids, context=context):
            # kittiu, if product line, we need to calculate carefully
            if this.product_id and not this.product_uos: # TODO: uos case is not covered yet.
                oline_qty = uom_obj._compute_qty(cr, uid, this.product_uom.id, this.product_uom_qty, this.product_id.uom_id.id)
                iline_qty = 0.0
                for iline in this.invoice_lines:
                    if iline.invoice_id.state != 'cancel':
                        if not this.product_uos: # Normal Case
                            iline_qty += uom_obj._compute_qty(cr, uid, iline.uos_id.id, iline.quantity, iline.product_id.uom_id.id)
                        else: # UOS case.
                            iline_qty += iline.quantity / (iline.product_id.uos_id and iline.product_id.uos_coeff or 1)                        
                # Test quantity
                res[this.id] = iline_qty >= oline_qty
            else:
                res[this.id] = this.invoice_lines and \
                all(iline.invoice_id.state != 'cancel' for iline in this.invoice_lines) 
        return res    

    # Overwrite method, need it because it is being called here.
    def _order_lines_from_invoice(self, cr, uid, ids, context=None):
        # direct access to the m2m table is the less convoluted way to achieve this (and is ok ACL-wise)
        cr.execute("""SELECT DISTINCT sol.id FROM sale_order_invoice_rel rel JOIN
                                                  sale_order_line sol ON (sol.order_id = rel.order_id)
                                    WHERE rel.invoice_id = ANY(%s)""", (list(ids),))
        return [i[0] for i in cr.fetchall()]

    from openerp.osv import fields, osv
    _columns = {
        'invoiced': fields.function(_fnct_line_invoiced, string='Invoiced', type='boolean',
            store={
                'account.invoice': (_order_lines_from_invoice, ['state'], 10),
                'sale.order.line': (lambda self,cr,uid,ids,ctx=None: ids, ['invoice_lines'], 10)}),
    }

class sale_billing_plan(models.Model):
    _name = "sale.billing.plan"
    _description = "Billing Plan"
    _order = "order_id,sequence,id"
    
    order_id = fields.Many2one('sale.order', string='Order Reference', readonly=True, index=True, ondelete='cascade', copy=False)
    order_line_id = fields.Many2one('sale.order.line', string='Order Line Reference', readonly=True, index=True, ondelete='cascade', copy=False)
    sequence = fields.Integer(string='Sequence', default=10, help="Gives the sequence of this line when displaying the billing plan.")
    installment = fields.Integer(string='Installment', help="Group of installment. Each group will be an invoice")
    date_invoice = fields.Date(string='Invoice Date', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', related='order_line_id.product_id', store=True, readonly=True,)
    name = fields.Text(string='Description', related='order_line_id.name', store=True, readonly=True,)    
    bill_percent = fields.Float(string='Percent', digits=(12,6))
    bill_amount = fields.Float(string='Amount', digits=dp.get_precision('Account'))
       
    @api.one
    @api.onchange('bill_percent')
    def _onchange_bill_percent(self):
        subtotal = self.order_line_id.price_subtotal
        self.bill_amount = subtotal and self.bill_percent/100 * subtotal or 0.0
        
    @api.one
    @api.onchange('bill_amount')
    def _onchange_bill_amount(self):
        subtotal = self.order_line_id.price_subtotal
        self.bill_percent = subtotal and (self.bill_amount / subtotal) * 100 or 0.0


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
