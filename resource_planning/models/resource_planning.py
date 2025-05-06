import logging
from datetime import timedelta

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourcePlanning(models.Model):
    _name = 'resource.planning'
    _description = 'Resource Planning'

    #name = fields.Char(compute="_compute_name",store=True)
    name = fields.Char()
    role_id = fields.Many2one(comodel_name="resource.role")
    week_template_id = fields.Many2one(comodel_name="resource.week.template")
    date_start = fields.Datetime()
    date_stop = fields.Datetime()

    def create_shifts(self):
        if self.week_template_id:
            week_template_ids = self.env["resource.week.template.shift"].search([("week_template_id", "=", self.week_template_id.id)])
            _logger.error(f"{week_template_ids=}")
            if week_template_ids:
                records = []
                for week_template_id in week_template_ids:
                    record = {"date_start": week_template_id.date_start, "duration": week_template_id.duration, "day": str(week_template_id.date_start.weekday())}
                    if self.role_id:
                        record.update({"role_id": self.role_id.id})
                    records.append(record)
                _logger.error(f"{records=}")
                self.env["resource.shift"].create(records)

    
    # @api.depends("date_start","date_stop")
    # def _compute_name(self):
    #     for record in self:
    #         if record.date_start and record.date_stop:
    #             record.name = f"{record.date_start} - {record.date_stop}"
    #         else:
    #             record.name = False