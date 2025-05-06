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
    role_id = fields.Many2one(comodel_name="resource.role")
    week_template_shift_ids = fields.One2many(comodel_name="resource.week.template.shift",inverse_name="week_template_id")

    def week_template_shift_action(self):
        action = {
        'type': 'ir.actions.act_window',
        'name': 'Week Template Shifts',
        'res_model': 'resource.week.template.shift',
        'view_mode': 'calendar',
        'target': 'current',
        'context': {
            'default_week_template_id': self.id
            },
        }
        return action