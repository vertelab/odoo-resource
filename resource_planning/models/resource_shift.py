import logging
from datetime import timedelta, datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ResourceShift(models.Model):
    _name = 'resource.shift'
    _description = 'Resource Shift'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    attendance_id = fields.Many2one(comodel_name="hr.attendance")
    color = fields.Integer()
    company_id = fields.Many2one(comodel_name='res.company',)
    date_start = fields.Datetime()
    date_stop = fields.Datetime(compute="_compute_date_stop",store=True)
    day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
        ], compute="_compute_day", store=True)
    department_id = fields.Many2one(related="plan_id.planning_id.department_id")
    duration = fields.Float()
    duration = fields.Float(string="Duration (Hours)",help="Shift duration in decimal hours",)
    employee_id = fields.Many2one(comodel_name="hr.employee", compute="_compute_employee_id",store=True)
    end_time = fields.Float(string="End Time", )
    hr_icon_display = fields.Selection(related='employee_id.hr_icon_display')
    image_128 = fields.Binary(related="employee_id.image_128")
    name = fields.Char(string="Shift Name", compute="_compute_name")
    plan_id = fields.Many2one(comodel_name="resource.plan")
    planning_id = fields.Many2one(related="plan_id.planning_id")
    res_users_id = fields.Many2one(comodel_name="res.users", related="resource_id.user_id")
    resource_id = fields.Many2one(comodel_name="resource.resource",group_expand="_group_expand_resource_id",domain="[('resource_type', '=', 'user')]")
    role_id = fields.Many2one(comodel_name="resource.role")
    show_hr_icon_display = fields.Boolean(related="employee_id.show_hr_icon_display")
    slot_id = fields.Many2one(comodel_name="resource.slot")
    start_time = fields.Float(string="Start Time", help="Shift start time (24-hour format)")
    status_color = fields.Integer(compute="compute_status_color")
    week_number = fields.Integer(compute="_compute_week_number", store=True)
    week_number_string = fields.Char(compute="_compute_week_number_string", store=True)
    week_start_date = fields.Datetime(compute="_compute_week_start_date",store=True)
    week_template_id = fields.Many2one(comodel_name="resource.week.template")
    worked_hours = fields.Float(related="attendance_id.worked_hours")


    def compute_status_color(self):
        for shift in self:
            shift.status_color = 0 # Grey
            if shift.resource_id:
                if shift.role_id.id != shift.resource_id.role_id.id:
                    shift.status_color = 1  # Red
                else:
                    shift.status_color = 10  # Green
            else:
                shift.status_color = 3  # Orange

    # ~ @api.constrains('role_id','resource_id')
    # ~ def _check_resource_role(self):
        # ~ for shift in self:
            # ~ if shift.resource_id:
                # ~ if shift.role_id.id != shift.resource_id.role_id.id:
                    # ~ raise UserError(_(f"{shift.resource_id.name} doesn't have the role {shift.role_id.name}."))

    @api.depends("date_start")
    def _compute_week_number(self):
        for record in self:
            record.week_number = record.date_start.isocalendar().week
    

    @api.depends("week_number")
    def _compute_week_number_string(self):
        for record in self:
            record.week_number_string = str(record.week_number)

    @api.depends("resource_id")
    def _compute_employee_id(self):
        for record in self:
            record.employee_id = record.resource_id.employee_id.id # employee_id is in this case a One2many field. Don't know why...

    @api.depends("plan_id.date_start")
    def _compute_week_start_date(self):
        for record in self:
            _logger.error(f"{record.plan_id=} {record.plan_id.date_start=}")
            if record.plan_id and record.plan_id.date_start:
                record.week_start_date = record.plan_id.date_start - timedelta(days=record.plan_id.date_start.weekday())
            else:
                record.week_start_date = datetime.now()

    @api.depends("date_start")
    def _compute_day(self):
        for record in self:
            record.day = str(record.date_start.weekday())
    
    @api.depends("duration","date_start")
    def _compute_date_stop(self):
        for record in self:
            if record.date_start and record.duration:
                record.date_stop = record.date_start + timedelta(hours=record.duration)
            else:
                record.date_stop = False

    @api.depends("date_start","date_stop","resource_id")
    def _compute_name(self):
        for record in self:
            if record.date_start and record.date_stop:
                record.name = f"{record.date_start.strftime('%H:%M')} - {record.date_stop.strftime('%H:%M')}"
                if record.role_id:
                    record.name = f"{dict(record._fields['day'].selection).get(record.day)} " + record.name
                if record.week_template_id:
                    record.name = f"{record.week_template_id.name} " + record.name
                if record.role_id:
                    record.name = f"{record.role_id.name} " + record.name
                if record.resource_id:
                    record.name = f"{record.resource_id.name} " + record.name
            else:
                record.name = False

    def action_assign_shifts(self):
        employees = self.env["resource.resource"].search([("role_id", "!=", False)])
        for employee in employees:
            weeks = self.env["resource.shift"].search([]).mapped("week_number")
            for week in weeks:
                role_shifts = self.env["resource.shift"].search([("role_id", "=", employee.role_id.id),("resource_id", "=", False),("week_number", "=", week)])
                for shift in role_shifts:
                    pass

    def _group_expand_resource_id(self, resource_id, domain):
        _logger.error(f"{domain=}")
        domain=[('resource_type', '=', 'user')]
        resource_ids = resource_id._search(domain)
        return self.env["resource.resource"].browse(resource_ids)
