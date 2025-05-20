import logging
from datetime import timedelta, datetime

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourcePlan(models.Model):
    _name = 'resource.plan'
    _description = 'Resource Plan'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char()
    planning_id = fields.Many2one(comodel_name="resource.plan")
    week_template_ids = fields.Many2many(comodel_name="resource.week.template")
    date_start = fields.Date()
    shift_ids = fields.One2many(comodel_name="resource.shift",inverse_name="plan_id")
    shift_count = fields.Integer(compute="_compute_shift_count")
    slot_ids = fields.One2many(comodel_name="resource.slot",inverse_name="plan_id")
    slot_count = fields.Integer(compute="_compute_slot_count")
    plan_role_ids = fields.One2many(comodel_name="resource.plan.role", inverse_name="plan_id")
    plan_resource_ids = fields.One2many(comodel_name="resource.plan.resource", inverse_name="plan_id")


    @api.depends("shift_ids")
    def _compute_shift_count(self):
        for record in self:
            record.shift_count = self.env["resource.shift"].search_count([('plan_id', '=', record.id)])
    
    @api.depends("slot_ids")
    def _compute_slot_count(self):
        for record in self:
            record.slot_count = self.env["resource.slot"].search_count([('plan_id', '=', record.id)])

    def action_get_shifts(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Shifts',
            'res_model': 'resource.shift',
            'view_mode': 'kanban,calendar,form,list,pivot',
            'target': 'current',
            'context': {'group_by':'resource_id'},
            'domain': [('plan_id', '=', self.id)]
        }
        return action

    def action_get_slots(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Slots',
            'res_model': 'resource.slot',
            'view_mode': 'kanban,form,list',
            'target': 'current',
            #'context': {},  # you can pass context here if needed
            'domain': [('plan_id', '=', self.id)]
        }
        return action

    def update_data_lines(self):
        self.update_plan_roles()
        self.update_plan_resources()

    def update_plan_roles(self):
        for plan_id in self:
            plan_id.plan_role_ids.unlink()
            role_ids = set(plan_id.shift_ids.mapped("role_id"))
            for role in role_ids:
                self.env["resource.plan.role"].create({"plan_id": plan_id.id, "role_id": role.id})

    def update_plan_resources(self):
        for plan_id in self:
            plan_id.plan_resource_ids.unlink()
            resource_ids = set(plan_id.shift_ids.mapped("resource_id"))
            for resource in resource_ids:
                self.env["resource.plan.resource"].create({"plan_id": plan_id.id, "resource_id": resource.id})


    def create_shifts(self):
        records = []
        if not self.week_template_ids:
            raise UserError(_("You need to have at least one week scheduled."))
        date_start = self.date_start
        for week_template_id in self.week_template_ids:
            _logger.error(f"{date_start.weekday()=}")
            for day_number in range(date_start.weekday(),7):
                shifts_this_day = list(filter(lambda w: w.week_number == day_number,week_template_id.week_template_shift_ids))
                if date_start.weekday() == day_number:
                    for shift in shifts_this_day:
                        new_date_start = datetime(date_start.year,date_start.month,date_start.day,shift.date_start.hour,shift.date_start.minute,shift.date_start.second)
                        record = {"date_start": new_date_start, "duration": shift.duration, "role_id": shift.role_id.id, "plan_id": self.id, "week_template_id": week_template_id.id}
                        records.append(record)
                date_start = date_start + timedelta(days=1)
        self.env["resource.shift"].create(records)

    def reset_date_start(self):
        if self.date_start.weekday() == 0:
            return self.date_start
        else:
            return self.date_start - timedelta(days=self.date_start.weekday())