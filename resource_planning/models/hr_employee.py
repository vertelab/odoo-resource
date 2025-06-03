from datetime import timedelta, datetime
from functools import partial
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone
import logging

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    role_ids = fields.Many2many(related="resource_id.role_ids")
    resource_shift_ids = fields.One2many(comodel_name="resource.shift", inverse_name="employee_id")
    resource_shift_count = fields.Integer(compute="_compute_resource_shift_count")

    def _compute_resource_shift_count(self):
        for record in self:
            record.resource_shift_count = len(record.resource_shift_ids)

    def get_shifts(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Shifts',
            'res_model': 'resource.shift',
            'view_mode': 'calendar,kanban,form,list,pivot',
            'target': 'current',
            'context': {'group_by':'resource_id'},
            'domain': [('employee_id', '=', self.id)]
        }
        return action

    def shift_fit(self,shift):
        overlapping_shifts = self.resource_shift_ids.filtered(
            lambda s: (
                    s.date_start < shift.date_stop and
                    shift.date_start < s.date_stop
                ))
        if not bool(overlapping_shifts):
            return False
        ok = self.resource_calendar_id._work_intervals_batch(timezone(self.tz or 'UTC').localize(shift.date_start),timezone(self.tz or 'UTC').localize( shift.date_stop),compute_leaves=True)
        return ok
        
