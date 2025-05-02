from odoo import models, fields, api
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone

class ResourceShiftSlot(models.Model):
    _name = 'resource.shift.slot'
    _description = 'Resource Shift Slot'

    planning_shift = fields.Many2one('resource.shift', string='Shift')
    
    role_id = fields.Many2one('resource.role', required=True, string="Role")
    

    resource_ids = fields.Many2many(
        'resource.resource',
        string="Assigned Resources",
        domain="[('id', 'in', role_resource_ids)]"  # Dynamic domain based on role_id
    )
    
    role_resource_ids = fields.Many2many(
        'resource.resource',
        compute='_compute_role_resource_ids',
        store=False,
        string="Role Resources"
    )
    
    name = fields.Char(
        compute='_compute_name',
        store=True,
        string="Shift Name"
    )
    
    start_date = fields.Datetime(
        string="Start Datetime",
        required=True,
        help="The starting date and time of the shift"
    )
    
    stop_date = fields.Datetime(
        string="Stop Datetime",
        required=True,
        help="The ending date and time of the shift"
    )
    
    duration = fields.Float(
        string="Duration (Hours)",
        help="Shift duration in decimal hours",
        readonly=True,
    )

    @api.depends('role_id')
    def _compute_role_resource_ids(self):
        """
        Compute the resources available for the selected role.
        """
        for slot in self:
            if slot.role_id:
                slot.role_resource_ids = slot.role_id.resource_ids
            else:
                slot.role_resource_ids = False



    @api.onchange('start_date', 'stop_date')
    def _onchange_start_stop_dates(self):
        """
        Automatically compute duration when start_date and stop_date are set.
        """
        if self.start_date and self.stop_date:
            user_tz = self.env.user.tz or 'UTC'  # Get user's timezone or default to UTC
            tz = timezone(user_tz)
            
            # Convert start_date and stop_date to user's timezone
            start_date_local = fields.Datetime.context_timestamp(self, self.start_date)
            stop_date_local = fields.Datetime.context_timestamp(self, self.stop_date)
            
            # Compute duration in hours
            delta = self.stop_date - self.start_date
            self.duration = delta.total_seconds() / 3600.0  # Convert seconds to hours

    @api.depends('start_date', 'stop_date', 'role_id')
    def _compute_name(self):
        """
        Compute the name based on role name, start time, and stop time.
        """
        for slot in self:
            if slot.role_id and slot.start_date and slot.stop_date:
                user_tz = self.env.user.tz or 'UTC'  # Get user's timezone or default to UTC
                tz = timezone(user_tz)
                
                # Convert start and stop dates to user's timezone
                start_time_local = fields.Datetime.context_timestamp(self, slot.start_date).strftime("%H:%M")
                stop_time_local = fields.Datetime.context_timestamp(self, slot.stop_date).strftime("%H:%M")
                
                slot.name = f"{slot.role_id.name} ({start_time_local} - {stop_time_local})"
            else:
                slot.name = "Undefined"
