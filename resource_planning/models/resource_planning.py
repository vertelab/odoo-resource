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

    name = fields.Char()
    plan_ids = fields.One2many(comodel_name="resource.plan", inverse_name="planning_id")
    date_start = fields.Datetime()
    date_stop = fields.Datetime()
    plan_count = fields.Integer(compute="_compute_plan_count")

    @api.depends("plan_ids")
    def _compute_plan_count(self):
        for record in self:
            record.plan_count = len(record.plan_ids)

    def get_plans(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Plans',
            'res_model': 'resource.plan',
            'view_mode': 'list,form,pivot',
            'target': 'current',
            'context': {'default_planning_id': self.id},
            'domain': [('planning_id', '=', self.id)]
        }
        return action

