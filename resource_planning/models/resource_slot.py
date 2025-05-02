from datetime import timedelta
from pytz import timezone

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ResourceSlot(models.Model):
    _name="resource.slot"
    _description="Resource Slot"

    name = fields.Char(compute="_compute_name",store=True)
    shift_id = fields.Many2one(comodel_name="resource.shift")
    project_id = fields.Many2one(comodel_name="project.project")
    date_start = fields.Datetime(string="Start Time")
    date_stop = fields.Datetime(string="End Time", compute="_compute_date_stop")
    duration = fields.Float()
    slot_resource_ids = fields.One2many(comodel_name="resource.slot.resource", inverse_name="slot_id")
    res_users_id = fields.Many2one(comodel_name="res.users")

    @api.depends("duration","date_start")
    def _compute_date_stop(self):
        for record in self:
            if record.date_start and record.duration:
                record.date_stop = record.date_start + timedelta(hours=record.duration)
            else:
                record.date_stop = False

    @api.depends("date_start","date_stop")
    def _compute_name(self):
        for record in self:
            if record.date_start and record.date_stop:
                record.name = f"{record.date_start} - {record.date_stop}"
            else:
                record.name = False
