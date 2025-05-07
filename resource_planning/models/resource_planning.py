import logging
from datetime import timedelta, datetime

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourcePlanning(models.Model):
    _name = 'resource.planning'
    _description = 'Resource Planning'

    name = fields.Char()
    week_template_ids = fields.Many2many(comodel_name="resource.week.template")
    date_start = fields.Date()

    def create_shifts(self):
        records = []
        date_start = self.reset_date_start()
        for week_template_id in self.week_template_ids:
            week_template_shift_ids = self.env["resource.week.template.shift"].search([('week_template_id', 'in', self.week_template_ids.ids)])
            for day_number in range(7):
                day_filter = filter(lambda w: w.week_number == day_number ,week_template_shift_ids)
                for day in day_filter:
                    new_date_start = datetime(date_start.year,date_start.month,date_start.day,day.date_start.hour,day.date_start.minute,day.date_start.second)
                    record = {"date_start": new_date_start, "duration": day.duration, "role_id": day.role_id.id}
                    records.append(record)
                date_start = date_start + timedelta(days=1)
            date_start = date_start + timedelta(days=1)
            
        self.env["resource.shift"].create(records)

    def reset_date_start(self):
        if self.date_start.weekday() == 0:
            return self.date_start
        else:
            return self.date_start - timedelta(days=self.date_start.weekday())