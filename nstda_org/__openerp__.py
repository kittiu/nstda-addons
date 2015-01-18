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
{
    'name' : 'NSTDA Organization Structure',
    'version' : '1.0',
    'author' : 'Ecosoft',
    'category' : 'Sales',
    'description' : """

This module create NSTDA organization structure,

  * Business Area
    * Sales Office
    * Profit Center
    * WBS/Project
    
Each of them will tie with Analytic Account, and will be available in every document.
This will allow them for Analytic view.

    """,
    'website': 'www.ecosoft.co.th',
    'depends' : ['sale',
                 'purchase',
                 'account',
                 'account_voucher',
                 'analytic'],
    'data': [
        "org_view.xml",
        "org_data.xml",
        "sale_view.xml",
        "account_invoice_view.xml"
    ],
    'qweb' : [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
