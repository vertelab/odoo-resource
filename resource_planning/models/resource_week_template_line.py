import logging
from datetime import datetime, timedelta

from odoo import models, fields, api
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from pytz import timezone

_logger = logging.getLogger(__name__)

class ResourceWeekTemplateLine(models.Model):
    _name = 'resource.week.template.line'
    _description = 'Resource Week Template Line'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    week_template_id = fields.Many2one(comodel_name="resource.week.template")
    #week_template_shift_id = fields.Many2one(comodel_name="resource.week.template.shift") 
    role_id = fields.Many2one(comodel_name='resource.role')  
    duration = fields.Float()