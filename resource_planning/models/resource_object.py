import logging

from odoo import models, fields, api
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class ResourceObject(models.Model):
    _name = 'resource.object'
    _description = 'Resource Object Template'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True,
        readonly=False
    )
    model_id = fields.Many2one(comodel_name='ir.model')
    model_name = fields.Char(related='model_id.model', string='Model Name', readonly=True, store=True)
    filter_domain = fields.Char(string='Record selection')
    order_by_field = fields.Many2one(
        'ir.model.fields',
        string='Order By Field',
        domain="[('model_id', '=', model_id)]"
    )
    
    eval_duration = fields.Text(
    string="Eval Duration",
    help="Python expression to compute duration. 'record' is the current record. Example: record.some_field * 2"
    )
    
    shift_object_ids = fields.One2many(
        'resource.slot',  
        'object_description_id',   
        string='Shift Slots'
    )
    
    def action_open_slots(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Shift Objects',
            'res_model': 'resource.slot',
            'view_mode': 'list,form',
            'domain': [('object_description_id', '=', self.id)],
            'context': {'default_object_description_id': self.id},
            'target': 'current',
        }

    @api.depends('model_id', 'filter_domain', 'order_by_field')
    def _compute_name(self):
        for rec in self:
            # Example logic: combine model name and filter domain
            model_part = rec.model_id.display_name if rec.model_id else ''
            filter_part = rec.filter_domain or ''
            order_part = rec.order_by_field.display_name if rec.order_by_field else ''
            # Compose the name as you wish
            rec.name = f"{model_part} | {filter_part} | {order_part}".strip(" |")
            
    def return_duration(self, record):
        self.ensure_one()
        if not self.eval_duration:
            return 1
        context = {'record': record}
        try:
            return safe_eval(self.eval_duration, context)
        except Exception as e:
            raise UserError(f"Error evaluating duration: {e}")
            
    def _get_domain_records(self):
        self.ensure_one()
        model_name = self.model_id.model
        domain = safe_eval(self.filter_domain or '[]')
        return self.env[model_name].search(domain)

    def create_slots(self):
        for object_description in self:
            records = object_description._get_domain_records()
            shift_object_model = object_description.env['resource.slot']
            _logger.warning(f"{records=}")
            for rec in records:
                reference = f"{rec._name},{rec.id}"
                # Check if a shift object with this reference_id already exists
                exists = shift_object_model.search([
                    ('reference_id', '=', reference),
                    ('object_description_id', '=', object_description.id)
                ], limit=1)
                _logger.warning(f"{exists=} {reference=}")
                if not exists:
                    vals = {
                        'reference_id': reference,
                        'object_description_id': object_description.id
                    }
                    new_obj = shift_object_model.create(vals)
                    new_obj._compute_duration()
        return True

    
    def action_open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Resource Object',
            'res_model': 'resource.object',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
        
        


 
