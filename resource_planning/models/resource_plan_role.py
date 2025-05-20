import logging
from datetime import timedelta, datetime

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourcePlanRole(models.Model):
    _name = 'resource.plan.role'
    _description = 'Resource Plan Role'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    plan_id = fields.Many2one(comodel_name="resource.plan")
    role_id = fields.Many2one(comodel_name="resource.role")
    shift_ids = fields.One2many(related="plan_id.shift_ids")
    duration= fields.Float(compute="_compute_duration")

    def _compute_duration(self):
        for record in self:
            filtered_shifts = record.shift_ids.filtered(lambda s: s.role_id.id == record.role_id.id)
            if filtered_shifts:
                record.duration = sum(filtered_shifts.mapped("duration"))
            else:
                record.duration = False