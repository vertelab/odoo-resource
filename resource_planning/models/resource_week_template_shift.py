import logging
from datetime import datetime, timedelta

from odoo import models, fields, api
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourceWeekTemplateShift(models.Model):
    _name = 'resource.week.template.shift'
    _description = 'Resource Week Template Shift'

    date_start = fields.Datetime(required=True)
    date_stop = fields.Datetime(compute="_compute_date_stop",store=True)
    duration = fields.Float()
    name = fields.Char(compute="_compute_name", store=True)
    week_template_id = fields.Many2one(comodel_name="resource.week.template",required=True)
    role_id = fields.Many2one(comodel_name="resource.role",required=True)
    week_number = fields.Integer(compute="_compute_week_number",store=True)

    day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], compute="_compute_day", store=True)

    @api.depends("week_number")
    def _compute_day(self):
        for record in self:
            record.day = str(record.week_number)

    @api.depends("duration","date_start")
    def _compute_date_stop(self):
        for record in self:
            if record.date_start and record.duration:
                record.date_stop = record.date_start + timedelta(hours=record.duration)
            else:
                record.date_stop = False
    
    @api.depends("date_start")
    def _compute_week_number(self):
        for record in self:
            record.week_number = record.date_start.weekday()

    @api.depends("date_start","date_stop")
    def _compute_name(self):
        for record in self:
            if record.date_start and record.date_stop:
                record.name = f"{record.date_start} - {record.date_stop}"
            else:
                record.name = False

    def action_template_shift_wizard(self):
        _logger.error(f"{self.env.context["default_week_template_id"]=}")
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Template Copy Shift Wizard',
            'res_model': 'week.template.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_week_template_id': self.env.context["default_week_template_id"]},
            #'domain': [('planning_id', '=', self.id)]
        }
        return action