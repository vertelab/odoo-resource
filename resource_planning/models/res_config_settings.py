from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_slots = fields.Boolean(string="Use Slots", help="If enabled, adds slot planning on shifts.", 
                                config_parameter='resource_planning.use_slots')
    plan_department = fields.Selection(selection=[("department_prioritized","Department Prioritized"),
                                                  ("department_and_non","Department and None Departments Only"),
                                                  ("department_only","Department Only")],config_parameter='resource_planning.plan_department')
    hour_day = fields.Float(
        string="Hours per Day",
        config_parameter='resource_planning.hour_day'
    )
    hours_week = fields.Float(
        string="Hours per Week",
        config_parameter='resource_planning.hours_week'
    )
