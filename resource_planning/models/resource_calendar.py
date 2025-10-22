import logging
from datetime import timedelta, datetime
from pytz import timezone

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class ResourcePlanResource(models.Model):
    _inherit = "resource.calendar"

    points = fields.Float(default=lambda self: self._set_default_points())

    def _set_default_points(self):
        return self.full_time_required_hours or 0.0