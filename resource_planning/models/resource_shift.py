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


    any_unassigned = fields.Boolean(compute="_compute_any_unassigned", store=False)
    @api.depends('plan_id')
    def _compute_any_unassigned(self):
        plan_ids = self.mapped('plan_id').ids
        domain = [('plan_id', 'in', plan_ids), ('resource_id', '=', False)]
        shifts_per_plan = self.env['resource.shift'].read_group(domain, ['plan_id'], ['plan_id'])
        plan_unassigned = {rec['plan_id'][0]: rec['plan_id_count'] > 0 for rec in shifts_per_plan}
        for rec in self:
            rec.any_unassigned = plan_unassigned.get(rec.plan_id.id, False)
    attendance_id = fields.Many2one(comodel_name="hr.attendance")
    check_in = fields.Datetime(related="attendance_id.check_in")
    check_out = fields.Datetime(related="attendance_id.check_out")
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
    employee_id = fields.Many2one(comodel_name="hr.employee", compute="_compute_employee_id",store=True)
    end_time = fields.Float(string="End Time", tracking=True)
    has_unassigned_shifts = fields.Boolean(related="plan_id.has_unassigned_shifts")    
    hr_icon_display = fields.Selection(related='employee_id.hr_icon_display')
    image_128 = fields.Binary(related="employee_id.image_128")
    is_has_resource_checkedin = fields.Selection(string="Absent", help="The shift has started and has the employee checked in?",selection=[('ok','OK'),('not','Resource Absent')],compute="_check_shift", tracking=True, default="ok")
    is_within_planner_calendar = fields.Selection(string="Planning Schema", selection=[('ok','OK'),('not','Out of Planning Schema')],compute="_check_shift",tracking=True, default="ok")
    is_within_resource_calendar = fields.Selection(string="Employee Schema", selection=[('ok','OK'),('not','Out of Resource Schema')],compute="_check_shift",tracking=True, default="ok")
    is_within_resource_dwt = fields.Selection(string="Day Worktime", selection=[('ok','OK'),('not','Out of Resource Day Worktime')],compute="_check_shift",tracking=True, default="ok")
    is_within_resource_role = fields.Selection(string="Role", selection=[('ok','OK'),('not','Out of Planning Schema')],compute="_check_shift",tracking=True, default="ok")
    is_within_resource_wwt = fields.Selection(string="Week Worktime", selection=[('ok','OK'),('not','Out of Resource Week Worktime')],compute="_check_shift",tracking=True, default="ok")
    is_current_week = fields.Boolean(compute="_compute_is_current_week",store=True)
    is_last_week = fields.Boolean(compute="_compute_is_last_week", store=True)
    is_next_week = fields.Boolean(compute="_compute_is_next_week", store=True)
    is_today = fields.Boolean(compute="_compute_is_today", store=True)
    name = fields.Char(string="Shift Name", compute="_compute_name", store=True)
    plan_id = fields.Many2one(comodel_name="resource.plan")
    planning_id = fields.Many2one(related="plan_id.planning_id")
    res_users_id = fields.Many2one(comodel_name="res.users", related="resource_id.user_id")
    resource_id = fields.Many2one(comodel_name="resource.resource",group_expand="_group_expand_resource_id",domain="[('resource_type', '=', 'user')]", tracking=True)
    role_id = fields.Many2one(comodel_name="resource.role", required=True, tracking=True)
    show_hr_icon_display = fields.Boolean(related="employee_id.show_hr_icon_display")
    slot_id = fields.Many2one(comodel_name="resource.slot")
    start_time = fields.Float(string="Start Time", help="Shift start time (24-hour format)", tracking=True)
    status_color = fields.Integer(compute="_check_shift")
    status_title = fields.Char(string="Shift Status",compute="_check_shift")
    week_number = fields.Integer(compute="_compute_week_number", store=True)
    week_number_string = fields.Char(compute="_compute_week_number_string", store=True)
    week_start_date = fields.Datetime(compute="_compute_week_start_date",store=True)
    week_template_id = fields.Many2one(comodel_name="resource.week.template")
    worked_hours = fields.Float(related="attendance_id.worked_hours")
    
    @api.depends("date_start","duration","resource_id")
    def _check_shift(self):
        for shift in self:
            if shift.resource_id:
                shift.status_color = 10 # Green
                shift.status_title = 'All is Hunky Dory' # Green
            else:
                shift.status_color = 0 # Gray
                shift.status_title = 'Not Assigned' # Green
            
            if shift.resource_id and not shift.plan_id.planning_id.shift_fit(shift):
                shift.is_within_planner_calendar = 'not'
                shift.status_color = 1 # Red
                shift.status_title = dict(shift._fields['is_within_planner_calendar'].selection).get(shift.is_within_planner_calendar, '')
            else:
                shift.is_within_planner_calendar = 'ok'

            if shift.resource_id and not shift.employee_id.shift_fit(shift):
                shift.is_within_resource_calendar = 'not'
                if not shift.status_color == 1:
                    shift.status_color = 3 # Orange
                    shift.status_title = dict(shift._fields['is_within_resource_calendar'].selection).get(shift.is_within_resource_calendar, '')
            else:
                shift.is_within_resource_calendar = 'ok'
           
            if shift.resource_id and not shift.role_id in shift.resource_id.role_ids:
                shift.is_within_resource_role = 'not'
                if not shift.status_color == 1:
                    shift.status_color = 3 # Orange
                    shift.status_title = dict(shift._fields['is_within_resource_role'].selection).get(shift.is_within_resource_role, '')
            else:
                shift.is_within_resource_role = 'ok'
            
            _logger.error(f"{shift.resource_allocation_week(shift.date_start,shift.resource_id,float(self.env['ir.config_parameter'].sudo().get_param('resource_planning.hours_week', 40.0)))}")
            
            if shift.resource_id and shift.resouce_allocation_date(shift.date_start,shift.resource_id) > float(self.env['ir.config_parameter'].sudo().get_param('resource_planning.hour_day', 11.0)):
                shift.is_within_resource_dwt = "not"
                shift.status_color = 3 # Orange
                shift.status_title = dict(shift._fields['is_within_resource_dwt'].selection).get(shift.is_within_resource_dwt, '')
            else:
                shift.is_within_resource_dwt = "ok"
            
            if shift.resource_id and shift.resource_allocation_week(shift.date_start,shift.resource_id,float(self.env['ir.config_parameter'].sudo().get_param('resource_planning.hours_week', 40.0))):
                shift.is_within_resource_wwt = "not"
                shift.status_color = 3 # Orange
                shift.status_title = dict(shift._fields['is_within_resource_wwt'].selection).get(shift.is_within_resource_wwt, '')
            else:
                shift.is_within_resource_wwt = "ok"
            
            if shift.resource_id and fields.Datetime.now() >= shift.date_start and not shift.check_in:
                shift.is_has_resource_checkedin = "not"
                shift.status_color = 1 # Red
                shift.status_title = dict(shift._fields['is_has_resource_checkedin'].selection).get(shift.is_has_resource_checkedin, '')
            else:
                shift.is_has_resource_checkedin = "ok"
            
    @api.depends("date_start")
    def _compute_is_today(self):
        for record in self:
            record.is_today = record.date_start.date() == datetime.now().date() 
 
    @api.depends("date_start")
    def _compute_week_number(self):
        for record in self:
            record.week_number = int(record.date_start.strftime('%V'))

    @api.depends("week_number")
    def _compute_week_number_string(self):
        for record in self:
            record.week_number_string = str(record.week_number)
    
    @api.depends("week_number")
    def _compute_is_current_week(self):
        for record in self:
            _logger.error(f"{record.week_number} {int(datetime.now().strftime('%V'))} {record.week_number == int(datetime.now().strftime('%V'))}")
            record.is_current_week = record.week_number == int(datetime.now().strftime('%V'))

    @api.depends("week_number")
    def _compute_is_next_week(self):
        for record in self:
            _logger.error(f"{record.week_number} {int(datetime.now().strftime('%V')) + 1} {record.week_number == int(datetime.now().strftime('%V')) + 1}")
            record.is_next_week = record.week_number == int(datetime.now().strftime('%V')) + 1
    
    @api.depends("week_number")
    def _compute_is_last_week(self):
        for record in self:
            _logger.error(f"{record.week_number} {int(datetime.now().strftime('%V')) - 1} {record.week_number == int(datetime.now().strftime('%V')) - 1}")
            record.is_last_week = record.week_number == int(datetime.now().strftime('%V')) - 1

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
                tz_date_start = self.make_tz_aware(record.date_start)
                tz_date_stop = self.make_tz_aware(record.date_stop)
                record.name = f"{tz_date_start.strftime('%H:%M')} - {tz_date_stop.strftime('%H:%M')}"
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

    def make_tz_aware(self,_date):
        tz = self.env.context.get('tz')
        return timezone("UTC").localize(_date).astimezone(timezone(tz))

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

    def resource_allocation_week(self, date, resource_id, wwt):
        week_start = date - timedelta(days=date.weekday())
        period_start = week_start - timedelta(weeks=15)
        period_end = week_start + timedelta(days=6)
        shifts = self.env['resource.shift'].search([
            ('date_start', '>=', period_start.strftime('%Y-%m-%d 00:00:00')),
            ('date_start', '<=', period_end.strftime('%Y-%m-%d 23:59:59')),
            ('resource_id', '=', resource_id.id)
        ])
        total_hours = sum(shifts.mapped('duration'))
        avg_weekly_hours = total_hours / 16.0
        return avg_weekly_hours > wwt

    def resouce_allocation_plan_role(self,plan_id,role_ids):
        return self.env['resource.shift'].search([('plan_id','=',plan_id.id),('role_id','in',role_ids),('resource_id','=',False)])
    
    def resource_non_parallell_date_role(self,date,role_id):
        all_shifts = self.env['resource.shift'].search([
                ('date_start','>=',date.strftime('%Y-%m-%d 00:00:00')),
                ('date_start','<=',date.strftime('%Y-%m-%d 23:59:59')),
                ('resource_id','=',False),
                ('role_id','=',role_id.id)])
        
        non_parallel_shifts = self.env['resource.shift']
        last_end = False
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
        last_end = False
        for shift in sorted_shifts.sorted(lambda d: d.date_start):
            if not last_end or shift.date_start >= last_end:
                non_parallel_shifts += shift
                last_end = shift.date_stop
        return non_parallel_shifts.sorted(lambda d: duration,reverse=True)
        
    def unset_resource(self):
        self.resource_id = False
        
        

