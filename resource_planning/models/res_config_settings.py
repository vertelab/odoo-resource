from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_planning_slots = fields.Boolean(string="Planning Slots", help="If enabled, adds slot planning on shifts.",compute="_compute_is_planning_slots")
    plan_department = fields.Selection(selection=[("department_prioritized","Department Prioritized"),("department_and_non","Department and None Departments Only"),("department_only","Department Only")],compute="_compute_plan_department")

    @api.depends("company_id")
    def _compute_is_planning_slots(self):
        param = self.env['ir.config_parameter'].sudo().get_param('your_module.your_field_name')
        for rec in self:
            rec.is_planning_slots = param

    @api.depends("company_id")
    def _compute_plan_department(self):
        param = self.env['ir.config_parameter'].sudo().get_param('your_module.your_field_name')
        for rec in self:
            rec.plan_department = param