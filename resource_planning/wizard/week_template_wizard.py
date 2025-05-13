import logging
from datetime import datetime, timedelta

from odoo import models, fields, api
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
        _logger.error(f"{self.week_template_id.week_template_shift_ids=}")
        shifts = list(map(lambda s: s.id,filter(lambda shift: shift.day == self.day, self.week_template_id.week_template_shift_ids)))
        _logger.error(f"{shifts=}")
        self.week_template_shift_ids = [(6,0, shifts)]

    def copy_days(self):
        days_check = [self.monday,self.tuesday,self.wednesday,self.thursday,self.friday,self.saturday,self.sunday]
        if any(days_check):
            records = []
            for shift in self.week_template_shift_ids:
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
                for day in days:
                    new_date_start = shift.date_start 
                    days_to_move = day - int(shift.day)
                    if 0 > days_to_move:
                        new_date_start = new_date_start - timedelta(days=abs(days_to_move))
                    else:
                        new_date_start = new_date_start + timedelta(days=days_to_move)
                    records.append({"date_start":new_date_start,"duration":shift.duration,"week_template_id":shift.week_template_id.id,"role_id":shift.role_id.id})
            return self.env["resource.week.template.shift"].create(records)
        raise UserError(_("You need to select one or more day/days to copy to!"))

