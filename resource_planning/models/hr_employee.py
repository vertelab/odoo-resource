import logging
from datetime import timedelta, datetime

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from pytz import timezone

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # role_ids = fields.Many2many(comodel_name="resource.role")
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
