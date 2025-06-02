import logging
from datetime import datetime, timedelta

from odoo import models, fields, api
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone
from pytz import all_timezones

_logger = logging.getLogger(__name__)

_tzs = [(tz, tz) for tz in sorted(all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]

class ResourceWeekTemplate(models.Model):
    _name = 'resource.week.template'
    _description = 'Resource Week Template'
    _inherit = ["mail.thread", "mail.activity.mixin"]  

    name = fields.Char(required=True)
    week_template_shift_ids = fields.One2many(comodel_name="resource.week.template.shift",inverse_name="week_template_id",copy=True,ondelete='cascade')
    week_template_shift_count = fields.Integer(compute="_compute_week_template_shift_count")
    week_template_line_ids = fields.One2many(comodel_name='resource.week.template.line',inverse_name='week_template_id')
    tz = fields.Selection(_tzs, string='Timezone', default=lambda self: self._context.get('tz'),
                          help="When printing documents and exporting/importing data, time values are computed according to this timezone.\n"
                               "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
                               "Anywhere else, time values are computed according to the time offset of your web client.")

    def update_template_lines(self):
        for template in self:
            template.week_template_line_ids.unlink()
            role_ids = set(template.week_template_shift_ids.mapped("role_id"))
            for role in role_ids:
                self.env["resource.week.template.line"].create({"week_template_id": template.id, "role_id": role.id})

    @api.depends("week_template_shift_ids")
    def _compute_week_template_shift_count(self):
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
