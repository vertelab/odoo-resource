import logging
from datetime import timedelta, datetime
from pytz import timezone

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    # shift_id = fields.Many2one(comodel_name="resource.shift")

    @api.model_create_multi
    def create(self, vals_list):
        attendance_ids = super().create(vals_list)
        self.connect_attendance_with_shift(attendance_ids)
        return attendance_ids

    def connect_attendance_with_shift(self,attendance_ids):
        for attendance_id in attendance_ids:
            _logger.error("test"*100)
            shifts = self.env["resource.shift"].search(
                [
                    ("date_start", ">=", datetime.combine(attendance_id.check_in.date(), datetime.min.time())), 
                    ("date_start", "<=", datetime.combine(attendance_id.check_in.date(), datetime.max.time())), 
                    ("employee_id", "=", attendance_id.employee_id.id),
                    ("attendance_id", "=", False)
                ])
            if not shifts:
                raise UserError(_("There seems to not be any shift to check in to."))
            closest_shift = min(shifts, key=lambda d: abs(d.date_start - attendance_id.check_in))
            closest_shift.attendance_id = attendance_id.id