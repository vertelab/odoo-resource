import logging
from datetime import timedelta, datetime

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourcePlanResource(models.Model):
    _name = 'resource.plan.resource'
    _description = 'Resource Plan Resource'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    plan_id = fields.Many2one(comodel_name="resource.plan")
    resource_id = fields.Many2one(comodel_name="resource.resource")
    shift_ids = fields.One2many(related="plan_id.shift_ids")
    duration = fields.Float(string="Planned Hours",compute="_compute_duration")
    worked_hours = fields.Float(compute="_compute_worked_hours") 

    def _compute_duration(self):
        for record in self:
            filtered_shifts = record.shift_ids.filtered(lambda s: s.resource_id.id == record.resource_id.id)
            if filtered_shifts:
                record.duration = sum(filtered_shifts.mapped("duration"))
            else:
                record.duration = False

    def _compute_worked_hours(self):
        for record in self:
            filtered_shifts = record.shift_ids.filtered(lambda s: s.resource_id.id == record.resource_id.id)
            if filtered_shifts:
                record.worked_hours = sum(filtered_shifts.mapped("worked_hours"))
            else:
                record.worked_hours = False
                
    def action_get_shifts_resource(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Shifts',
            'res_model': 'resource.shift',
            'view_mode': 'kanban,calendar,form,list,pivot',
            'target': 'current',
            'context': {'search_default_plan_id': self.plan_id.id,'search_default_resource_id': self.resource_id.id},
        }
        
    def action_get_slot_resource(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Slots',
            'res_model': 'resource.slot',
            'view_mode': 'kanban,calendar,form,list,pivot',
            'target': 'current',
            'context': {'search_default_plan_id': self.plan_id.id,'search_default_resource_id': self.resource_id.id},
        }

