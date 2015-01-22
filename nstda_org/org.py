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

class business_area(models.Model):
    _name = "business.area"
    _description = "Business Area"
    _inherits = {'account.analytic.account': "analytic_account_id"}
    
    code = fields.Char(string='Code', index=True)
    name = fields.Char(string='Name')
    company_id = fields.Many2one('res.company', string='Company', ondelete='restrict',
        required=True, default=lambda self: self.env['res.company']._company_default_get('business.area'))
    analytic_account_id = fields.Many2one('account.analytic.account', 'Business Area/Analytic',
            ondelete='cascade', required=True, auto_join=True)
    user_ids = fields.Many2many('res.users', 'business_area_user_rel', 'business_area_id', 'user_id',
            string='Users', copy=False)
    sale_office_ids = fields.One2many('sale.office', 'business_area_id', string='Sales Offices', copy=False)
    profit_center_ids = fields.One2many('profit.center', 'business_area_id', string='Profit Centers', copy=False)

    _sql_constraints = [
        ('code_uniq', 'unique(code)',
            'Code must be unique!'),
    ]
    
    @api.model
    def create(self, vals):
        if not vals.get('type', False) or vals.get('type') not in ('business_area'):
            vals['type'] = 'business_area'
        self = self.with_context(code=vals['code'], name=vals['name'])
        return super(business_area, self).create(vals)


class branch(models.Model):
    _name = "branch"
    _description = "Branch"
    _inherits = {'account.analytic.account': "analytic_account_id"}
    
    code = fields.Char(string='Code', index=True)
    name = fields.Char(string='Name')
    company_id = fields.Many2one('res.company', string='Company', ondelete='restrict',
        required=True, default=lambda self: self.env['res.company']._company_default_get('branch'))
    analytic_account_id = fields.Many2one('account.analytic.account', 'Branch/Analytic',
            ondelete='cascade', required=True, auto_join=True)
    sale_office_ids = fields.One2many('sale.office', 'branch_id', string='Sales Office', copy=False)

    _sql_constraints = [
        ('code_uniq', 'unique(code)',
            'Code must be unique!'),
    ]
    
    @api.model
    def create(self, vals):
        if not vals.get('type', False) or vals.get('type') not in ('branch'):
            vals['type'] = 'branch'
        self = self.with_context(code=vals['code'], name=vals['name'])
        return super(branch, self).create(vals)

class sale_office(models.Model):
    _name = "sale.office"
    _description = "Sales Office"
    _inherits = {'account.analytic.account': "analytic_account_id"}
    
    code = fields.Char(string='Code', index=True)
    name = fields.Char(string='Name')
    company_id = fields.Many2one('res.company', string='Company', ondelete='restrict',
        required=True, default=lambda self: self.env['res.company']._company_default_get('sale.office'))
    analytic_account_id = fields.Many2one('account.analytic.account', 'Business Area/Analytic',
            ondelete='cascade', required=True, auto_join=True)
    branch_id = fields.Many2one('branch', string='Branch', ondelete='restrict',
        required=True)
    business_area_id = fields.Many2one('business.area', string='Business Area', ondelete='restrict',
        required=True)
    
    _sql_constraints = [
        ('code_uniq', 'unique(code)',
            'Code must be unique!'),
    ]
    
    @api.model
    def create(self, vals):
        if not vals.get('type', False) or vals.get('type') not in ('sale_office'):
            vals['type'] = 'sale_office'
        self = self.with_context(code=vals['code'], name=vals['name'])
        return super(sale_office, self).create(vals)


class profit_center(models.Model):
    _name = "profit.center"
    _description = "Profit Center"
    _inherits = {'account.analytic.account': "analytic_account_id"}
    
    code = fields.Char(string='Code', index=True)
    name = fields.Char(string='Name')
    company_id = fields.Many2one('res.company', string='Company', ondelete='restrict',
        required=True, default=lambda self: self.env['res.company']._company_default_get('profit.center'))
    analytic_account_id = fields.Many2one('account.analytic.account', 'Business Area/Analytic',
            ondelete='cascade', required=True, auto_join=True)
    business_area_id = fields.Many2one('business.area', string='Business Area', ondelete='restrict',
        required=True)
    wbs_project_ids = fields.One2many('wbs.project', 'profit_center_id', string='WBS/Projects', copy=False)

    _sql_constraints = [
        ('code_uniq', 'unique(code)',
            'Code must be unique!'),
    ]
    
    @api.model
    def create(self, vals):
        if not vals.get('type', False) or vals.get('type') not in ('profit_center'):
            vals['type'] = 'profit_center'
        self = self.with_context(code=vals['code'], name=vals['name'])
        return super(profit_center, self).create(vals)
    

class wbs_project(models.Model):
    _name = "wbs.project"
    _description = "WBS/Project"
    _inherits = {'account.analytic.account': "analytic_account_id"}
    
    code = fields.Char(string='Code', index=True)
    name = fields.Char(string='Name')
    company_id = fields.Many2one('res.company', string='Company', ondelete='restrict',
        required=True, default=lambda self: self.env['res.company']._company_default_get('wbs.project'))
    analytic_account_id = fields.Many2one('account.analytic.account', 'Business Area/Analytic',
            ondelete='cascade', required=True, auto_join=True)
    profit_center_id = fields.Many2one('profit.center', string='Profit Center', ondelete='restrict',
        required=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)',
            'Code must be unique!'),
    ]
    
    @api.model
    def create(self, vals):
        if not vals.get('type', False) or vals.get('type') not in ('wbs_project'):
            vals['type'] = 'wbs_project'
        self = self.with_context(code=vals['code'], name=vals['name'])
        return super(wbs_project, self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
