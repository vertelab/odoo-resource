from odoo import models, fields, api

class ResourceShift(models.Model):
    _name = 'resource.shift'
    _description = 'Resource Shift'

    name = fields.Char(string="Shift Name")
    role_id = fields.Many2one('resource.role', required=True, string="Role")
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
    date_stop = fields.Datetime()


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
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for shift in self:
            if shift.end_time and shift.start_time:
                shift.duration = shift.end_time - shift.start_time
            else:
                shift.duration = 0

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
