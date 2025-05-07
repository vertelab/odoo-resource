import logging
from datetime import timedelta
from pytz import timezone

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

MODELS_LIST = ["project.project"]

class ResourceSlot(models.Model):
    _name="resource.slot"
    _description="Resource Slot"


    name = fields.Char(compute="_compute_name",store=True)
    shift_id = fields.Many2one(comodel_name="resource.shift")
    project_id = fields.Many2one(comodel_name="project.project")
    ref_object = fields.Reference(string='Object', selection=lambda m: [(model.model, model.name) for model in
                                                                       m.env['ir.model'].sudo().search([('model','in',MODELS_LIST)])])
    date_start = fields.Datetime(string="Start Time")
    date_stop = fields.Datetime(string="End Time", compute="_compute_date_stop")
    duration = fields.Float()
    #slot_resource_ids = fields.One2many(comodel_name="resource.slot.resource", inverse_name="slot_id" )
    resource_id = fields.Many2one(comodel_name="resource.resource",group_expand="_group_expand_resource_id",domain="[('resource_type', '=', 'user')]")
    res_users_id = fields.Many2one(comodel_name="res.users")
    role_id = fields.Many2one(comodel_name="resource.role")

    @api.depends("duration","date_start")
    def _compute_date_stop(self):
        for record in self:
            if record.date_start and record.duration:
                record.date_stop = record.date_start + timedelta(hours=record.duration)
            else:
                record.date_stop = False

    @api.depends("date_start","date_stop")
    def _compute_name(self):
        for record in self:
            if record.date_start and record.date_stop:
                record.name = f"{record.date_start} - {record.date_stop}"
            else:
                record.name = False

    def _group_expand_resource_id(self, resource_id, domain):
        _logger.error(f"{domain=}")
        domain=[('resource_type', '=', 'user')]
        resource_ids = resource_id._search(domain)
        return self.env["resource.resource"].browse(resource_ids)
