import logging

from odoo import models, fields, api
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourceShiftTemplate(models.Model):
    _name = 'resource.shift.template'
    _description = 'Resource Shift Template'

    date_start = fields.Datetime()
    date_stop = fields.Datetime()
    duration = fields.Float()
    
