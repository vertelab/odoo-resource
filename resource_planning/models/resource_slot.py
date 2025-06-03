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
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute="_compute_name",store=True)
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
    plan_id = fields.Many2one(comodel_name="resource.plan")
    shift_id = fields.Many2one('resource.shift',string='Shift',required=False,ondelete='cascade')
    object_description_id = fields.Many2one('resource.object',string='Object Description',required=True,ondelete='cascade')
    
    reference_id = fields.Reference(
        selection='_reference_models',
        string='Reference'
    )
    duration = fields.Float(string='Duration')
    
    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True
    )
    
    reference_model = fields.Char(
        string="Reference Model",
        compute='_compute_reference_model',
        store=True,
        index=True
    )


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
        
    @api.depends('reference_id')
    def _compute_reference_model(self):
        for rec in self:
            rec.reference_model = rec.reference_id._name if rec.reference_id else False

    @api.model
    def _reference_models(self):
        model_ids = self.env['ir.model'].search([('transient', '=', False)])
        return [(model.model, model.name) for model in model_ids if 'name' in model.field_id.mapped('name')]

    @api.depends('reference_id')
    def _compute_name(self):
        for rec in self:
            if rec.reference_id:
                # This will call the record's display_name (usually the 'name' field or _rec_name)
                rec.name = rec.reference_id.display_name
            else:
                rec.name = False
    
    def _compute_duration(self):
        for rec in self:
            if rec.object_description_id:
               rec.duration = rec.object_description_id.return_duration(rec)
                
    def action_open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Resource Shift Object',
            'res_model': 'resource.slot',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

