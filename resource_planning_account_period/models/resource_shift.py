from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ResourceShift(models.Model):
    _inherit = 'resource.shift'

    is_current_fiscal_year = fields.Boolean(compute="_compute_is_current_fiscal_year",store=True)
    is_next_fiscal_year = fields.Boolean(compute="_compute_is_next_fiscal_year",store=True)   

    @api.depends("date_start")
    def _compute_is_current_fiscal_year(self):
        current_date = date.today()
        fiscal_year_id = self.env["account.fiscal.year"].search([("date_from", "<=", current_date),("date_to", ">=", current_date)],limit=1)
        for shift in self:
            if fiscal_year_id:
                if fiscal_year_id.date_from <= shift.date_start.date() and fiscal_year_id.date_to >= shift.date_start.date():
                    shift.is_current_fiscal_year = True
                else:
                    shift.is_current_fiscal_year = False
            else:
                shift.is_current_fiscal_year = False
            
    @api.depends("date_start")
    def _compute_is_next_fiscal_year(self):
        current_date = date.today()
        current_fiscal_year_id = self.env["account.fiscal.year"].search([("date_from", "<=", current_date),("date_to", ">=", current_date)],limit=1)
        next_fiscal_year_id = False
        if current_fiscal_year_id:
            next_fiscal_year_id = self.env["account.fiscal.year"].search([("date_from", "=", current_fiscal_year_id.date_to + timedelta(days=1))],limit=1)
        for shift in self:
            if next_fiscal_year_id:
                if next_fiscal_year_id.date_from <= shift.date_start.date() and next_fiscal_year_id.date_to >= shift.date_start.date():
                    shift.is_next_fiscal_year = True
                else:
                    shift.is_next_fiscal_year = False
            else:
                shift.is_next_fiscal_year = False

                
    def recompute_stored_fields(self):
        super(ResourceShift,self).recompute_stored_fields()
        self._compute_is_current_fiscal_year()
        self._compute_is_next_fiscal_year()
