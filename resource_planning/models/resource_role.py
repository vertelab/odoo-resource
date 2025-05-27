import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class ResourceRole(models.Model):
    _name = 'resource.role'
    _description = 'Resource Role'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True)
    description = fields.Html()
    resource_ids = fields.Many2many(
        comodel_name='resource.resource',
        string="Available Resources"
    )
    resource_type = fields.Selection([
        ('user', 'Human'),
        ('material', 'Material')], string='Type',
        default='user', required=True)
