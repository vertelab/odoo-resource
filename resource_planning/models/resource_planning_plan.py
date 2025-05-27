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

    planning_id = fields.Many2one(comodel_name="resource.planning")
    plan_ids = fields.One2many(related="planning_id.plan_ids")
    duration = fields.Float(string="Planned Hours",compute="_compute_duration")
    worked_hours = fields.Float(compute="_compute_worked_hours") 

    def _compute_duration(self):
        for record in self:
            filtered_shifts = record.plan_ids.filtered(lambda s: s.resource_id.id == record.resource_id.id)
            if filtered_shifts:
                record.duration = sum(filtered_shifts.mapped("duration"))
            else:
                record.duration = False

    def _compute_worked_hours(self):
        for record in self:
            filtered_shifts = record.shift_ids.filtered(lambda s: s.resource_id.id == record.resource_id.id)
            if filtered_shifts:
                record.worked_hours = sum(filtered_shifts.mapped("worked_hours"))
            else:
                record.worked_hours = False

