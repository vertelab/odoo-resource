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

    date_start = fields.Date()
    date_stop = fields.Date()
    duration= fields.Float(string="Planned Hours",compute="_compute_duration")
    name = fields.Char()
    plan_resource_ids = fields.One2many(comodel_name="resource.plan.resource", inverse_name="plan_id")
    plan_role_ids = fields.One2many(comodel_name="resource.plan.role", inverse_name="plan_id")
    planning_id = fields.Many2one(comodel_name="resource.planning")
    shift_count = fields.Integer(compute="_compute_shift_count")
    shift_ids = fields.One2many(comodel_name="resource.shift",inverse_name="plan_id")
    slot_count = fields.Integer(compute="_compute_slot_count")
    slot_ids = fields.One2many(comodel_name="resource.slot",inverse_name="plan_id")
    week_template_ids = fields.Many2many(comodel_name="resource.week.template")
    worked_hours = fields.Float(compute="_compute_worked_hours") 

    def action_open_assign_objects_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Objects to Shifts',
            'res_model': 'resource.plan.object.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'active_ids': self.ids,
            },
        }


    def _compute_duration(self):
        for record in self:
            if record.shift_ids:
                record.duration = sum(record.shift_ids.mapped("duration"))
            else:
                record.duration = False
                
    def _compute_worked_hours(self):
        for record in self:
            if record.shift_ids:
                record.worked_hours = sum(record.shift_ids.mapped("worked_hours"))
            else:
                record.worked_hours = False

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
            'context': {'group_by':'resource_id','search_default_plan_id': self.id},
        }
        return action

    def action_get_slots(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Slots',
            'res_model': 'resource.slot',
            'view_mode': 'kanban,form,list',
            'target': 'current',
            'context': {'group_by':'resource_id','search_default_plan_id': self.id},
            # ~ 'domain': [('plan_id', '=', self.id)]
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
        date_start = self.date_start
        records = []
        stop_loop = False  # break both loops
        for week_template_id in self.week_template_ids:
            if stop_loop:
                break
            _logger.error(f"{date_start.weekday()=}")
            for day_number in range(date_start.weekday(), 7):
                shifts_this_day = list(filter(lambda w: w.week_number == day_number, week_template_id.week_template_shift_ids))
                if date_start.weekday() == day_number:
                    for shift in shifts_this_day:
                        new_date_start = datetime(
                            date_start.year, date_start.month, date_start.day,
                            shift.date_start.hour, shift.date_start.minute, shift.date_start.second
                        )
                        record = {
                            "date_start": new_date_start,
                            "duration": shift.duration,
                            "role_id": shift.role_id.id,
                            "plan_id": self.id,
                            "week_template_id": week_template_id.id
                        }
                        records.append(record)
                date_start = date_start + timedelta(days=1)
                if date_start > self.date_stop:
                    stop_loop = True
                    break
        self.env["resource.shift"].create(records)

    def reset_date_start(self):
        if self.date_start.weekday() == 0:
            return self.date_start
        else:
            return self.date_start - timedelta(days=self.date_start.weekday())

    def get_shift_role_ids(self):
        return set(self.env['resource.shift'].search([('plan_id','=',self.id)]).mapped('role_id'))

    def get_unallocated_shift(self):
        return self.env['resource.shift'].search([('plan_id','=',self.id),('resource_id','=',False)])

    def get_prioritized_resources(self):
        employee_department = freelance_department = self.env['hr.employee']
        if self.planning_id.department_id:
            employee_department = self.env["hr.employee"].search([('employee_type','in',['employee','worker','contractor']),('department_id','=',self.planning_id.department_id.id)])
            freelance_department = self.env["hr.employee"].search([('employee_type','in',['freelance','student','trainee']),('department_id','=',self.planning_id.department_id.id)])
        employee_all = self.env["hr.employee"].search([('employee_type','in',['employee','worker','contractor'])])
        freelance_all = self.env["hr.employee"].search([('employee_type','in',['freelance','student','trainee'])])
                
        return (employee_department | freelance_department | employee_all | freelance_all).sorted(key=lambda r: (
                                        0 if r in employee_department else
                                        1 if r in freelance_department else
                                        2 if r in employee_all else
                                        3
                                    ))
                            
