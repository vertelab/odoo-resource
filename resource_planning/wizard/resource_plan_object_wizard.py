import logging
from datetime import datetime, timedelta

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ResourcePlanObjectWizard(models.TransientModel):
    _name = 'resource.plan.object.wizard'
    _description = 'Resource Plan Object Wizard'

    def assign_objects_to_shifts(self):
        active_id = self.env.context.get('active_id')
        if not active_id:
            raise UserError("No active resource plan found.")
        plan = self.env['resource.plan'].browse(active_id)
        # Do something with plan
        for shift in plan.shift_ids:
            for resource_object in shift.role_id.mapped('resource_object_ids'):
                resource_object.create_resource_shift_objects()
                if shift.assigned_duration >= shift.duration:
                    break
                
                objects = self.env['resource.shift.object'].search([('object_description_id', '=', resource_object.id),('shift_id','=',False)])
                if resource_object.order_by_field:
                    order_field_name = resource_object.order_by_field.name
                objects = objects.sorted(key=lambda rec: getattr(rec.reference_id, order_field_name) or datetime.max)

                for object_record in objects:
                    if object_record.duration < (shift.duration - shift.assigned_duration):
                       _logger.warning(f"{object_record.duration=}")
                       _logger.warning(f"{shift.duration=}")
                       _logger.warning(f"{shift.assigned_duration=}")
                       _logger.warning(f"{(shift.duration - shift.assigned_duration)=}")
                       _logger.warning(f"{object_record.duration < (shift.duration - shift.assigned_duration)=}")
                       object_record.shift_id = shift
                
            
            

            

