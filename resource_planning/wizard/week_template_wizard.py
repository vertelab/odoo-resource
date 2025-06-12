import logging
from datetime import datetime, timedelta
from pytz import timezone
from pytz import all_timezones

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class WeekTemplateWizard(models.TransientModel):
    _name = 'week.template.wizard'
    _description = 'Resource Week Template Wizard'

    week_template_id = fields.Many2one(comodel_name="resource.week.template")
    week_template_shift_ids = fields.Many2many(comodel_name="resource.week.template.shift")
    day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ])
    monday = fields.Boolean()
    tuesday = fields.Boolean()
    wednesday = fields.Boolean()
    thursday = fields.Boolean()
    friday = fields.Boolean()
    saturday = fields.Boolean()
    sunday = fields.Boolean()

    @api.onchange("day")
    def get_shift_on_day(self):
        shifts = list(map(lambda s: s.id,filter(lambda shift: shift.day == self.day, self.week_template_id.week_template_shift_ids)))
        self.week_template_shift_ids = [(6,0, shifts)]

    def copy_days(self):
        days = self.get_selected_days()
        if not days:
            raise UserError(_("You need to select one or more day/days to copy to!"))
            
        if not self.week_template_shift_ids:
            raise UserError(_("No shift to copy from selected!"))
            
        if any(int(day) in days for day in self.week_template_shift_ids.mapped("day")):
            raise UserError(_("You can't copy shifts to the same day as the selected day"))
        
        [self.env["resource.week.template.shift"].search([("day", "=", day)]).unlink() for day in days]
        
        records = []
        for shift in self.week_template_shift_ids:
            for day in days:
                new_date_start = shift.date_start 
                days_to_move = day - int(shift.day)
                if 0 > days_to_move:
                    new_date_start = new_date_start - timedelta(days=abs(days_to_move))
                else:
                    new_date_start = new_date_start + timedelta(days=days_to_move)
                records.append({
                    "date_start":new_date_start,
                    "duration":shift.duration,
                    "week_template_id":shift.week_template_id.id,
                    "role_id":shift.role_id.id
                    })
        return self.env["resource.week.template.shift"].create(records)

    def get_selected_days(self):
        days = []
        if self.monday:
            days.append(0)
        if self.tuesday:
            days.append(1)
        if self.wednesday:
            days.append(2)
        if self.thursday:
            days.append(3)
        if self.friday:
            days.append(4)
        if self.saturday:
            days.append(5)
        if self.sunday:
            days.append(6)
        return days

    

