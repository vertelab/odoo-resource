import logging
from datetime import timedelta, datetime

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from pytz import timezone

_logger = logging.getLogger(__name__)

class Resource(models.Model):
    _inherit = 'resource.resource'

    # role_ids = fields.Many2many(comodel_name="resource.role")
    role_id = fields.Many2one(comodel_name="resource.role")
