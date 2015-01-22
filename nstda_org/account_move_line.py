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


class account_move_line(models.Model):
    _inherit = 'account.move.line'

#     def _prepare_analytic_line(self, cr, uid, obj_line, context=None):
#         """
#         Prepare the values given at the create() of account.analytic.line upon the validation of a journal item having
#         an analytic account. This method is intended to be extended in other modules.
# 
#         :param obj_line: browse record of the account.move.line that triggered the analytic line creation
#         """
#         return {'name': obj_line.name,
#                 'date': obj_line.date,
#                 'account_id': obj_line.analytic_account_id.id,
#                 'unit_amount': obj_line.quantity,
#                 'product_id': obj_line.product_id and obj_line.product_id.id or False,
#                 'product_uom_id': obj_line.product_uom_id and obj_line.product_uom_id.id or False,
#                 'amount': (obj_line.credit or  0.0) - (obj_line.debit or 0.0),
#                 'general_account_id': obj_line.account_id.id,
#                 'journal_id': obj_line.journal_id.analytic_journal_id.id,
#                 'ref': obj_line.ref,
#                 'move_id': obj_line.id,
#                 'user_id': uid,
#                }
    @api.v7
    def create_analytic_lines(self, cr, uid, ids, context=None):
        """ Method overwrite """
        acc_ana_line_obj = self.pool.get('account.analytic.line')
        for obj_line in self.browse(cr, uid, ids, context=context):
            if obj_line.analytic_lines:
                # Only delete 1 line, the one with analytic_account_id
                del_ids = []
                for obj in obj_line.analytic_lines:
                    if obj.account_id == obj_line.analytic_account_id:
                        del_ids.append(obj.id)
                acc_ana_line_obj.unlink(cr,uid,del_ids)
            if obj_line.analytic_account_id:
                if not obj_line.journal_id.analytic_journal_id:
                    raise osv.except_osv(_('No Analytic Journal!'),_("You have to define an analytic journal on the '%s' journal!") % (obj_line.journal_id.name, ))
                vals_line = self._prepare_analytic_line(cr, uid, obj_line, context=context)
                acc_ana_line_obj.create(cr, uid, vals_line)
            # 
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
