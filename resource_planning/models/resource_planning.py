import logging
from datetime import timedelta

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourcePlanning(models.Model):
    _name = 'resource.planning'
    _description = 'Resource Planning'

    name = fields.Char(compute="_compute_name",store=True)
    week_template_ids = fields.Many2many(comodel_name="resource.week.template")
    role_id = fields.Many2one(comodel_name="resource.role")
    date_start = fields.Datetime()
    date_stop = fields.Datetime()

    def create_shifts(self):
        if self.role_id and self.date_start and self.date_stop:
            week_template_ids = self.env["resource.week.template"].search([])
            _logger.error(f"{week_template_ids=}")
            if week_template_ids:
                week_temps = list(filter(lambda week_temp: week_temp.date_start > self.date_start and week_temp.date_stop < self.date_stop,week_template_ids))
                _logger.error(f"{week_temps=}")
                records = []
                for week_template_id in week_temps:
                    record = {"date_start": week_template_id.date_start, "duration": week_template_id.duration, "role_id": self.role_id.id}
                    records.append(record)
                _logger.error(f"{records=}")
                self.env["resource.shift"].create(records)

    
    @api.depends("date_start","date_stop")
    def _compute_name(self):
        for record in self:
            if record.date_start and record.date_stop:
                record.name = f"{record.date_start} - {record.date_stop}"
            else:
                record.name = False