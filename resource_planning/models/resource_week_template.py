import logging
from datetime import datetime, timedelta

from odoo import models, fields, api
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourceWeekTemplate(models.Model):
    _name = 'resource.week.template'
    _description = 'Resource Week Template'

    name = fields.Char(required=True)
    week_template_shift_ids = fields.One2many(comodel_name="resource.week.template.shift",inverse_name="week_template_id",copy=True)
    week_template_shift_count = fields.Integer(compute="compute_week_template_shift_count")
    week_template_line_ids = fields.One2many('resource.week.template.line','week_template_id',compute="create_stuff")


    def compute_week_template_line_ids(self):
        for record in self:
            role_ids = record.week_template_shift_ids.mapped("role_id")
            for role_id in role_ids:
                role_shifts = filter(lambda r: r.role_id.id == role_id.id,record.week_template_shift_ids)
                sum(role_shifts.mapped("duration"))

    @api.depends("week_template_shift_ids")
    def compute_week_template_shift_count(self):
        for record in self:
            record.week_template_shift_count = len(record.week_template_shift_ids)


    def week_template_shift_action(self):
        _logger.error(f"{self.env.context=}")
        action = {
        'type': 'ir.actions.act_window',
        'name': 'Week Template Shifts',
        'res_model': 'resource.week.template.shift',
        'view_mode': 'calendar,kanban,list,pivot',
        'target': 'current',
        'context': {
            'default_week_template_id': self.id,
            'calendar_default_date': '2025-01-01',
            },
        'domain': [('week_template_id','=',self.id)]
        }
        return action