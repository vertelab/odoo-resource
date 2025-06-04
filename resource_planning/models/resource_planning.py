import logging
from datetime import timedelta, datetime, date

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
import pytz
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourcPlanning(models.Model):
    _name = 'resource.planning'
    _description = 'Resource Planning'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    

    _tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]

    active = fields.Boolean(default=True)
    color = fields.Integer()
    company_id = fields.Many2one(comodel_name="res.company")
    date_start = fields.Datetime()
    date_stop = fields.Datetime()
    department_id = fields.Many2one(comodel_name="hr.department",group_expand="_group_expand_department_id")
    image_128 = fields.Binary()
    name = fields.Char()
    plan_count = fields.Integer(compute="_compute_plan_count")
    plan_ids = fields.One2many(comodel_name="resource.plan", inverse_name="planning_id")
    resource_calendar_id = fields.Many2one(comodel_name="resource.calendar",tracking=True)
    status_color = fields.Integer(compute="compute_status_color")
    shift_date = fields.Date()
    shift_ids = fields.One2many(comodel_name="resource.shift", inverse_name="planning_id", compute="_compute_shift_ids")
    tz = fields.Selection(_tzs, string='Timezone', default=lambda self: self._context.get('tz'),
                          help="When printing documents and exporting/importing data, time values are computed according to this timezone.\n"
                               "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
                               "Anywhere else, time values are computed according to the time offset of your web client.")
    use_slots = fields.Boolean(compute="_compute_use_slots")

    def _compute_use_slots(self):
        use_slots = self.env['ir.config_parameter'].sudo().get_param('resource_planning.use_slots', 'False') == 'True'
        for rec in self:
            rec.use_slots = use_slots
    
    def make_tz_aware(self,_date):
        tz = self.env.context.get('tz')
        return timezone("UTC").localize(_date).astimezone(timezone(tz))
    
    @api.depends("shift_date")
    def _compute_shift_ids(self):
        for record in self:
            if record.shift_date:
                record.shift_ids = self.env["resource.shift"].search([
                ("date_start", ">=", datetime(record.shift_date.year, record.shift_date.month, record.shift_date.day)),
                ("date_start", "<", datetime(record.shift_date.year, record.shift_date.month, record.shift_date.day + 1)),
                ("resource_id", "!=", False),
                ("check_in", "!=", False),
                ("check_out", "!=", False),
                ])
            else: 
                record.shift_ids = False
                
                
    def compute_status_color(self):
        for shift in self:
            shift.status_color = 0 # Grey
            shift.status_color = 3 # Orange
            # ~ if shift.resource_id:
                # ~ if shift.role_id.id != shift.resource_id.role_id.id:
                    # ~ shift.status_color = 1  # Red
                # ~ else:
                    # ~ shift.status_color = 10  # Green
            # ~ else:
                # ~ shift.status_color = 3  # Orange


    def _get_tz(self):
        # Finds the first valid timezone in his tz, his work hours tz,
        #  the company calendar tz or UTC and returns it as a string
        self.ensure_one()
        return self.tz or\
               self.resource_calendar_id.tz or\
               self.company_id.resource_calendar_id.tz or\
               'UTC'


    @api.depends("plan_ids")
    def _compute_plan_count(self):
        for record in self:
            record.plan_count = len(record.plan_ids)
        
    def action_staff_register_wizard(self):
        self.shift_date = date.today()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Staff Register Wizard',
            'res_model': 'resource.planning',
            'view_mode': 'form',
            "res_id": self.id,
            'view_id': self.env.ref('resource_planning.staff_register_wizard_view').id,
            'target': 'new',
        }
        return action

    def get_plans(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Plans',
            'res_model': 'resource.plan',
            'view_mode': 'list,form,calendar,pivot',
            'target': 'current',
            'context': {'search_default_planning_id': self.id},
        }
        return action

    def get_today(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Today',
            'res_model': 'resource.shift',
            'view_mode': 'calendar,list,form,kanban,pivot',
            'target': 'current',
            'context': {'search_default_planning_id': self.id},
        }
        return action
    def get_today_slots(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Today',
            'res_model': 'resource.slot',
            'view_mode': 'calendar,list,form,kanban,pivot',
            'target': 'current',
            'context': {'search_default_planning_id': self.id},
        }
        return action


    def get_this_week(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Plans',
            'res_model': 'resource.shift',
            'view_mode': 'calendar,kanban,list,form,pivot',
            'target': 'current',
            'context': {'search_default_this_week': True,'search_default_planning_id': self.id},
        }
        return action


    def _group_expand_department_id(self, resource_id, domain):
        _logger.error(f"{domain=}")
        # ~ domain=[('resource_type', '=', 'user')]
        # ~ resource_ids = resource_id._search(domain)
        
        return self.env["hr.department"].search([])

    def shift_fit(self,shift):
        if not shift:
            return
        if shift.resource_id:
            ok = self.resource_calendar_id._work_intervals_batch(pytz.timezone(self.tz or 'UTC').localize(shift.date_start),pytz.timezone(self.tz or 'UTC').localize(shift.date_stop),compute_leaves=True)
        else:
            ok = False
        return ok
        
