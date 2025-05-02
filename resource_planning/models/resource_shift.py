from datetime import timedelta

from odoo import models, fields, api

class ResourceShift(models.Model):
    _name = 'resource.shift'
    _description = 'Resource Shift'

    name = fields.Char(string="Shift Name")
    role_id = fields.Many2one('resource.role', required=True, string="Role")
    # day = fields.Selection([
    #     ('0', 'Monday'),
    #     ('1', 'Tuesday'),
    #     ('2', 'Wednesday'),
    #     ('3', 'Thursday'),
    #     ('4', 'Friday'),
    #     ('5', 'Saturday'),
    #     ('6', 'Sunday')
    # ], required=True)

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
            for _ in range(int(shift.duration/shift.slot_size)):
                if start_time not in start_times:
                    self.env["resource.slot"].create({"date_start": start_time, "duration": shift.slot_size})
                start_time = start_time + timedelta(hours=shift.slot_size)

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

    # @api.depends('role_id', 'start_time', 'end_time')
    # def _compute_name(self):
    #     for shift in self:
    #         if shift.role_id and shift.start_time and shift.end_time:
    #             # Format start and end times to HH:MM
    #             start_time_formatted = "{:02d}:{:02d}".format(
    #                 int(shift.start_time), int((shift.start_time % 1) * 60)
    #             )
    #             end_time_formatted = "{:02d}:{:02d}".format(
    #                 int(shift.end_time), int((shift.end_time % 1) * 60)
    #             )
    #             shift.name = f"{shift.role_id.name} ({start_time_formatted} - {end_time_formatted})"
    #         else:
    #             shift.name = "Undefined"
