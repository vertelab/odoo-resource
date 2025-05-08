from datetime import timedelta

from odoo import models, fields, api

class ResourceShift(models.Model):
    _name = 'resource.shift'
    _description = 'Resource Shift'

    name = fields.Char(string="Shift Name", compute="_compute_name")
    role_id = fields.Many2one(comodel_name="resource.role")
    planning_id = fields.Many2one(comodel_name="resource.planning")
    slot_id = fields.Many2one(comodel_name="resource.slot")
    resource_id = fields.Many2one(comodel_name="resource.resource", related="slot_id.resource_id")
    date_start = fields.Datetime()
    date_stop = fields.Datetime(compute="_compute_date_stop",store=True)
    duration = fields.Float()

    @api.model_create_multi
    def create(self, vals_list):
        shift_ids = super(ResourceShift,self).create(vals_list)
        self.create_slot(shift_ids)
        return shift_ids

    def create_slot(self,shift_ids=False):
        if not shift_ids:
            shift_ids = self
        for shift in shift_ids:
            record = {"date_start": shift.date_start, "duration": shift.duration, "role_id": shift.role_id.id, "planning_id": shift.planning_id.id}
            slot_id = self.env["resource.slot"].create(record)
            shift.slot_id = slot_id.id

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

    @api.depends("date_start","date_stop","resource_id")
    def _compute_name(self):
        for record in self:
            if record.date_start and record.date_stop:
                record.name = f"{record.date_start.strftime('%H:%M')} - {record.date_stop.strftime('%H:%M')}"
                if record.resource_id:
                    record.name = f"{record.resource_id.name} " + record.name
            else:
                record.name = False