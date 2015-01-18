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
from openerp import models, fields, api, _

class account_analytic_account(models.Model):

    _inherit = 'account.analytic.account'
    
    @api.v7
    def __init__(self, pool, cr):
        super(account_analytic_account, self).__init__(pool, cr)
        options = [('business_area', 'Business Area'),
                   ('sale_office', 'Sales Office'),
                   ('profit_center', 'Profit Center'),
                   ('wbs_project', 'WBS/Project')]
        type_selection = self._columns['type'].selection
        for option in options:
            if option not in type_selection:
                type_selection.append(option)

    @api.model
    def create(self, vals):
        todos = ['code', 'name']
        for key in todos:
            if (key not in vals.keys()) and self._context.get(key, False):
                vals[key] = self._context.get(key)
        return super(account_analytic_account, self).create(vals)

account_analytic_account()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
