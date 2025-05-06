import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ResourceRole(models.Model):
    _name = 'resource.role'
    _description = 'Resource Role'

    name = fields.Char(required=True)
    description = fields.Html()
    amount = fields.Integer()
    shift_ids = fields.One2many(comodel_name="resource.shift",inverse_name="role_id")
    resource_week_template_id = fields.Many2one(comodel_name="resource.week.template")
    resource_ids = fields.Many2many(
        comodel_name='resource.resource',
        string="Available Resources"
    )