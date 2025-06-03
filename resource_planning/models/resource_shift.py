from datetime import timedelta, datetime, time
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from pytz import timezone
import logging

_logger = logging.getLogger(__name__)

class ResourceShift(models.Model):
    _name = 'resource.shift'
    _description = 'Resource Shift'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    attendance_id = fields.Many2one(comodel_name="hr.attendance")
    color = fields.Integer()
    company_id = fields.Many2one(comodel_name='res.company',)
    date_start = fields.Datetime(tracking=True)
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
    duration = fields.Float(string="Duration (Hours)",help="Shift duration in decimal hours",tracking=True)
    assigned_duration = fields.Float(string="Assigned Duration (Hours)",help="Shift duration in decimal hours",compute="compute_assigned_duration",store=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", compute="_compute_employee_id",store=True)
    end_time = fields.Float(string="End Time", tracking=True)
    hr_icon_display = fields.Selection(related='employee_id.hr_icon_display')
    image_128 = fields.Binary(related="employee_id.image_128")
    name = fields.Char(string="Shift Name", compute="_compute_name", store=True)
    plan_id = fields.Many2one(comodel_name="resource.plan")
    planning_id = fields.Many2one(related="plan_id.planning_id")
    department_id = fields.Many2one(related="plan_id.planning_id.department_id")
    res_users_id = fields.Many2one(comodel_name="res.users", related="resource_id.user_id")
    resource_id = fields.Many2one(comodel_name="resource.resource",group_expand="_group_expand_resource_id",domain="[('resource_type', '=', 'user')]", tracking=True)
    role_id = fields.Many2one(comodel_name="resource.role", required=True, tracking=True)
    show_hr_icon_display = fields.Boolean(related="employee_id.show_hr_icon_display")
    slot_id = fields.Many2one(comodel_name="resource.slot")
    start_time = fields.Float(string="Start Time", help="Shift start time (24-hour format)", tracking=True)
    status_color = fields.Integer(compute="compute_status_color")
    week_number = fields.Integer(compute="_compute_week_number", store=True)
    week_number_string = fields.Char(compute="_compute_week_number_string", store=True)
    week_start_date = fields.Datetime(compute="_compute_week_start_date",store=True)
    week_template_id = fields.Many2one(comodel_name="resource.week.template")
    worked_hours = fields.Float(related="attendance_id.worked_hours")
    shift_object_ids = fields.One2many('resource.shift.object','shift_id',string='Shift Objects')
    
    def action_view_shift_objects(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assigned Objects',
            'res_model': 'resource.shift.object',
            'view_mode': 'list,form',
            'domain': [('shift_id', '=', self.id)],
            'context': {'default_shift_id': self.id},
        }
    
    @api.depends("shift_object_ids")
    def compute_assigned_duration(self):
        for shift in self:
            shift.assigned_duration = sum(shift.shift_object_ids.mapped("duration"))
        
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

    @api.depends("date_start","date_stop","resource_id","role_id")
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
        active_domain = self.env.context.get('active_domain', [])
        plan = self.env['resource.plan'].browse(next((v for (field, op, v) in active_domain if field == 'plan_id' and op == '='), None))
        active_domain.append(('resource_id', '=', False))
        
        nbr = 0
        while self.env['resource.shift'].search_count(active_domain) > 0 and nbr < 30:
            shifts = self.env['resource.shift'].search(active_domain)
            roles = set(shifts.mapped('role_id'))
            for employee in plan.get_prioritized_resources():
                _logger.warning(f"{employee.name} {nbr=} {roles=}")
                for shift in shifts:
                    if shift.role_id in employee.role_ids and employee.resource_calendar_id._work_intervals_batch(
                                    timezone(employee.tz or 'UTC').localize(shift.date_start),
                                    timezone(employee.tz or 'UTC').localize( shift.date_stop),
                                    compute_leaves=True):
                        overlapping_shifts = employee.resource_shift_ids.filtered(
                                lambda s: (
                                        s.date_start <= shift.date_stop and
                                        shift.date_start <= s.date_stop
                                    ))
                        if not bool(overlapping_shifts):
                            shift.write({'resource_id': employee.id})
            nbr += 1
            

    def _filter_unique_shifts(self,shifts):
        overlapping_shifts = set()
        for check_shift in shifts:
            for shift in shifts:
                if check_shift.date_start >= shift.date_start and check_shift.date_start < shift.date_stop:
                    overlapping_shifts.add(check_shift.id)
        unique_shifts = shifts.filtered(lambda s: s.id not in overlapping_shifts)
        _logger.error(f"{unique_shifts=}")
        return unique_shifts

    def _group_expand_resource_id(self, resource_id, domain):
        _logger.error(f"{domain=}")
        # ~ domain=[('resource_type', '=', 'user')]
        # ~ resource_ids = resource_id._search(domain)
        plan_id = None
        for item in domain:
            if isinstance(item, (list, tuple)) and len(item) == 3:
                field, op, v = item
                if field == 'plan_id' and op == '=':
                    plan_id = v
                    break
        plan = self.env['resource.plan'].browse(plan_id) if plan_id else None
        role_id = None
        for item in domain:
            if isinstance(item, (list, tuple)) and len(item) == 3:
                field, op, v = item
                if field == 'role_id' and op == '=':
                    role_id = v
                    break
        role = self.env['resource.role'].browse(role_id) if role_id else None
        department_id = None
        for item in domain:
            if isinstance(item, (list, tuple)) and len(item) == 3:
                field, op, v = item
                if field == 'department_id' and op == '=':
                    department_id = v
                    break
        department = self.env['hr.department'].browse(department_id) if department_id else None
        _logger.error(f"{department=} {role=} {plan=}")
        if department:
            return self.env["resource.resource"].browse(plan.get_prioritized_resources().filtered(lambda e: e.department_id.id == department_id).mapped('resource_id.id'))
        if role:
            return self.env["resource.resource"].browse(plan.get_prioritized_resources().filtered(lambda e: role in e.role_ids).mapped('resource_id.id'))
        if plan:
            return self.env["resource.resource"].browse(plan.get_prioritized_resources().mapped('resource_id.id'))
        return self.env["resource.resource"].search([])
        

    def resouce_allocation_date(self,date,resource_id):
        return sum(self.env['resource.shift'].search([
                ('date_start','>=',date.strftime('%Y-%m-%d 00:00:00')),
                ('date_start','<=',date.strftime('%Y-%m-%d 23:59:59')),
                ('resource_id','=',resource_id.id)]).mapped('duration'))
    
    def resouce_allocation_plan_role(self,plan_id,role_ids):
        return self.env['resource.shift'].search([('plan_id','=',plan_id.id),('role_id','in',role_ids),('resource_id','=',False)])
    
    def resource_non_parallell_date_role(self,date,role_id):
        all_shifts = self.env['resource.shift'].search([
                ('date_start','>=',date.strftime('%Y-%m-%d 00:00:00')),
                ('date_start','<=',date.strftime('%Y-%m-%d 23:59:59')),
                ('resource_id','=',False),
                ('role_id','=',role_id.id)])
        
        non_parallel_shifts = self.env['resource.shift']
        last_end = None
        for shift in all_shifts.sorted(lambda d: d.date_start):
            if not last_end or shift.date_start >= last_end:
                non_parallel_shifts += shift
                last_end = shift.date_stop
        return non_parallel_shifts.sorted(lambda d: d.duration,reverse=True)

    def plan_resouce_non_parallell_date_role(self,date,role_id):
        all_shift = self.env['resource.shift'].search([
                ('date_start','>=',date.strftime('%Y-%m-%d 00:00:00')),
                ('date_start','<=',date.strftime('%Y-%m-%d 23:59:59')),
                ('resource_id','=',False),
                ('role_id','=',role_id.id)])
        
        non_parallel_shifts = self.env['resource.shift']
        last_end = None
        for shift in sorted_shifts.sorted(lambda d: d.date_start):
            if not last_end or shift.date_start >= last_end:
                non_parallel_shifts += shift
                last_end = shift.date_stop
        return non_parallel_shifts.sorted(lambda d: duration,reverse=True)
        
