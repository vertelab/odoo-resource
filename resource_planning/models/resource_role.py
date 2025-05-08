import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ResourceRole(models.Model):
    _name = 'resource.role'
    _description = 'Resource Role'

    name = fields.Char(required=True)
    description = fields.Html()
    resource_ids = fields.Many2many(
        comodel_name='resource.resource',
        string="Available Resources"
    )