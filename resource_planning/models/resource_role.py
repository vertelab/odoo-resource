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
    resource_ids = fields.Many2many(
        comodel_name='resource.resource',
        string="Available Resources"
    )

    @api.model_create_multi
    def create(self, vals_list):
        role_ids = super(ResourceRole,self).create(vals_list)
        for role_id in role_ids:
            record_days = []
            for day in range(5):
                record = {
                    "role_id": role_id.id,
                    "day": str(day),
                    "start_time": 8,
                    "end_time": 17,
                }
                record_days.append(record)
            self.env["resource.shift"].create(record_days)
        return role_ids

