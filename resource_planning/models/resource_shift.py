import logging
from datetime import timedelta, datetime

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ResourceShift(models.Model):
    _name = 'resource.shift'
    _description = 'Resource Shift'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Shift Name", compute="_compute_name")
    role_id = fields.Many2one(comodel_name="resource.role")
    plan_id = fields.Many2one(comodel_name="resource.plan")
    slot_id = fields.Many2one(comodel_name="resource.slot")
    employee_id = fields.Many2one(comodel_name="hr.employee", compute="_compute_employee_id",store=True)
    res_users_id = fields.Many2one(comodel_name="res.users", related="resource_id.user_id")
    week_template_id = fields.Many2one(comodel_name="resource.week.template")
    resource_id = fields.Many2one(comodel_name="resource.resource",group_expand="_group_expand_resource_id",domain="[('resource_type', '=', 'user')]")
    week_start_date = fields.Datetime(compute="_compute_week_start_date",store=True)
    date_start = fields.Datetime()
    date_stop = fields.Datetime(compute="_compute_date_stop",store=True)
    duration = fields.Float()
    day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], compute="_compute_day", store=True)

    start_time = fields.Float(
        string="Start Time",
        help="Shift start time (24-hour format)"
    )
    end_time = fields.Float(
        string="End Time",
    )
    duration = fields.Float(
        string="Duration (Hours)",
        help="Shift duration in decimal hours",
    )

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


    def _group_expand_resource_id(self, resource_id, domain):
        _logger.error(f"{domain=}")
        domain=[('resource_type', '=', 'user')]
        resource_ids = resource_id._search(domain)
        return self.env["resource.resource"].browse(resource_ids)