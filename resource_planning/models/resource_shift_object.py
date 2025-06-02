from datetime import timedelta, datetime, time
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from pytz import timezone
import logging

_logger = logging.getLogger(__name__)

class ResourceShiftObject(models.Model):
    _name = 'resource.shift.object'
    _description = 'Resource Slot Object'

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
            'res_model': 'resource.shift.object',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

