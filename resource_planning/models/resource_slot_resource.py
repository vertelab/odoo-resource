from odoo import models, fields, api
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone

class ResourceSlotResource(models.Model):
    _name="resource.slot.resource"
    _description="Resource Slot Resource"
    
    slot_id = fields.Many2one(comodel_name="resource.slot")
    resource_id = fields.Many2one(comodel_name="resource.resource")
