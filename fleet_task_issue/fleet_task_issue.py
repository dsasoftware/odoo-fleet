# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    added by stella.fredo@gmail.com
#    based on Fleet analytic account by CLEARCORP S.A. <http://clearcorp.co.cr> and AURIUM TECHNOLOGIES <http://auriumtechnologies.com>
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
import logging
_logger = logging.getLogger(__name__)


class FleetVehicle(models.Model):

    _inherit = 'fleet.vehicle'


    @api.model
    def create(self, vals):
        acount_obj=self.env['account.analytic.account']
        fleet_id = super(FleetVehicle, self).create(vals)
        account_id=acount_obj.create({'name':self._vehicle_name_get(fleet_id)})
        fleet_id.write({'analytic_account_id':account_id.id})
        return fleet_id

    @api.multi
    def _count_vehicle_task(self):
        project_obj = self.env['project.project']
        self.task_count=len(project_obj.search([('analytic_account_id', '=', self.analytic_account_id.id)]).task_ids)

    @api.multi
    def _count_vehicle_issue(self):
        issue_obj = self.env['project.project']
        self.issue_count=len(issue_obj.search([('analytic_account_id', '=', self.analytic_account_id.id)]).issue_ids)


    @api.multi
    def write(self, vals):
        acount_obj=self.env['account.analytic.account']
        res = False
        for record in self:
            if not record.analytic_account_id:
                account_id=acount_obj.create({'name':record._vehicle_name_get(record)})
                vals.update({'analytic_account_id':account_id.id})
            record.analytic_account_id.write({'name':record.name,'use_tasks':True,'use_issues':True})
            project_id = self.env['project.project'].search([('analytic_account_id', '=', record.analytic_account_id.id)])
            vals.update({'project_id': project_id.id})
            res = super(FleetVehicle, record).write(vals)
        return res

    @api.model
    def _vehicle_name_get(self,record):
        res=(record.model_id.brand_id.name or '') + '/' + (record.model_id.name or '') + '/' + (record.license_plate or '')
        return res

    @api.multi
    def action_view_tasks(self):
        res = self.env['ir.actions.act_window'].for_xml_id('project', 'act_project_project_2_project_task_all')
        res['context'] = {
                'search_default_project_id': [self.project_id.id],
                'default_project_id': self.project_id.id,
            }
        return res

    project_id = fields.Many2one(comodel_name='project.project', string='Project', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    task_count = fields.Integer(compute=_count_vehicle_task, string="Vehicle Tasks" , multi=True)
    issue_count = fields.Integer(compute=_count_vehicle_issue, string="Vehicle Issues" , multi=True)


class  fleet_vehicle_log_services(models.Model):

    _inherit = 'fleet.vehicle.log.services'
    invoice_id = fields.Many2one('account.invoice',string='Facture')
