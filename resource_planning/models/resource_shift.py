from datetime import timedelta

from odoo import models, fields, api

class ResourceShift(models.Model):
    _name = 'resource.shift'
    _description = 'Resource Shift'

    name = fields.Char(string="Shift Name")
    role_id = fields.Many2one(comodel_name="resource.role")
    planning_id = fields.Many2one(comodel_name="resource.planning")
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
    duration = fields.Float()
    #slot_size = fields.Float(required=True,default=2)
    slot_ids = fields.One2many(comodel_name="resource.slot",inverse_name="shift_id")

    @api.model_create_multi
    def create(self, vals_list):
        shift_ids = super(ResourceShift,self).create(vals_list)
        self.create_slot(shift_ids)
        return shift_ids

    def create_slot(self,shift_ids=False):
        records = []
        if not shift_ids:
            shift_ids = self
        for shift in shift_ids:
            record = {"date_start": shift.date_start, "duration": shift.duration, "role_id": shift.role_id.id}
            records.append(record)
        if records:
            self.env["resource.slot"].create(records)

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