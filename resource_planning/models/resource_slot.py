from odoo import models, fields, api
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone

class ResourceSlot(models.Model):
    _name="resource.slot"
    _description="Resource Slot"

    name = fields.Char()
    shift_id = fields.Many2one(comodel_name="planning.shift")
    project_id = fields.Many2one(comodel_name="project.project")
    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="End Time")
    slot_resource_ids = fields.One2many(comodel_name="resource.slot.resource", inverse_name="slot_id")
    res_users_id = fields.Many2one(comodel_name="res.users")
