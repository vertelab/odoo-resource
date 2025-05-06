from datetime import timedelta

from odoo import models, fields, api

class ResourceShift(models.Model):
    _name = 'resource.shift'
    _description = 'Resource Shift'

    name = fields.Char(string="Shift Name")
    role_id = fields.Many2one('resource.role', string="Role")
    day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')
    ], required=True)

    date_start = fields.Datetime()
    date_stop = fields.Datetime(compute="_compute_date_stop",store=True)
    slot_size = fields.Float(required=True,default=2)
    slot_ids = fields.One2many(comodel_name="resource.slot",inverse_name="shift_id")

    @api.model_create_multi
    def create(self, vals_list):
        shift_ids = super(ResourceShift,self).create(vals_list)
        self.create_slot(shift_ids)
        return shift_ids

    def create_slot(self,shift_ids=False):
        if not shift_ids:
            shift_ids = self
        for shift in shift_ids:
            start_times = shift.slot_ids.mapped("date_start")
            start_time = shift.date_start
            loop_runs = 0
            remaining_time = shift.duration % shift.slot_size 
            real_slot_size = shift.slot_size
            shift_slot_size_is_bigger = shift.slot_size > shift.duration
            if shift_slot_size_is_bigger:
                loop_runs = 1
                real_slot_size = shift.duration
            elif shift.slot_size <= shift.duration:
                loop_runs = int(shift.duration / shift.slot_size)

            for _ in range(loop_runs):
                if start_time not in start_times:
                    self.env["resource.slot"].create({"date_start": start_time, "duration": shift.slot_size})
                start_time = start_time + timedelta(hours=shift.slot_size)

            if not shift_slot_size_is_bigger and remaining_time:
                if start_time not in start_times:
                    self.env["resource.slot"].create({"date_start": start_time, "duration": remaining_time})

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
    
    @api.depends("duration","date_start")
    def _compute_date_stop(self):
        for record in self:
            if record.date_start and record.duration:
                record.date_stop = record.date_start + timedelta(hours=record.duration)
            else:
                record.date_stop = False