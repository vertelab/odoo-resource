import logging
from datetime import timedelta, datetime

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourcPlanning(models.Model):
    _name = 'resource.planning'
    _description = 'Resource Planning'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    color = fields.Integer()
    company_id = fields.Many2one(comodel_name="res.company")
    date_start = fields.Datetime()
    date_stop = fields.Datetime()
    department_id = fields.Many2one(comodel_name="hr.department",group_expand="_group_expand_department_id")
    image_128 = fields.Binary()
    name = fields.Char()
    plan_count = fields.Integer(compute="_compute_plan_count")
    plan_ids = fields.One2many(comodel_name="resource.plan", inverse_name="planning_id")
    status_color = fields.Integer(compute="compute_status_color")
    active = fields.Boolean(default=True)

    def compute_status_color(self):
        for shift in self:
            shift.status_color = 0 # Grey
            shift.status_color = 3 # Orange
            # ~ if shift.resource_id:
                # ~ if shift.role_id.id != shift.resource_id.role_id.id:
                    # ~ shift.status_color = 1  # Red
                # ~ else:
                    # ~ shift.status_color = 10  # Green
            # ~ else:
                # ~ shift.status_color = 3  # Orange

    @api.depends("plan_ids")
    def _compute_plan_count(self):
        for record in self:
            record.plan_count = len(record.plan_ids)

    def get_plans(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Plans',
            'res_model': 'resource.plan',
            'view_mode': 'list,form,calendar,pivot',
            'target': 'current',
            'context': {'search_default_planning_id': self.id},
        }
        return action

    def get_today(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Today',
            'res_model': 'resource.shift',
            'view_mode': 'calendar,list,form,kanban,pivot',
            'target': 'current',
            'context': {'search_default_planning_id': self.id},
        }
        return action


    def get_this_week(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Plans',
            'res_model': 'resource.shift',
            'view_mode': 'calendar,kanban,list,form,pivot',
            'target': 'current',
            'context': {'search_default_planning_id': self.id},
        }
        return action


    def _group_expand_department_id(self, resource_id, domain):
        _logger.error(f"{domain=}")
        # ~ domain=[('resource_type', '=', 'user')]
        # ~ resource_ids = resource_id._search(domain)
        
        return self.env["hr.department"].search([])
