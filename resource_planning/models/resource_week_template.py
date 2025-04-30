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

    date_start = fields.Datetime()
    date_stop = fields.Datetime(compute="_compute_date_stop",store=True)
    duration = fields.Float()
    name = fields.Char(compute="_compute_name", store=True)

    @api.depends("duration","date_start")
    def _compute_date_stop(self):
        for record in self:
            if record.date_start and record.duration:
                record.date_stop = record.date_start + timedelta(hours=record.duration)
            else:
                record.date_stop = False

    #planning_id = fields.Many2one(comodel_name="resource.planning")
    # shift_template_id = fields.Many2one(comodel_name="resource.shift.template")
    
    @api.depends("date_start","date_stop")
    def _compute_name(self):
        for record in self:
            if record.date_start and record.date_stop:
                record.name = f"{record.date_start} - {record.date_stop}"
            else:
                record.name = False