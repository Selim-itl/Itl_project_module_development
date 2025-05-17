from odoo import models, fields

class IrActionsActWindow(models.Model):
    _inherit = 'project.task'

    progress = fields.Integer("Progress")
    assigned = fields.Many2many("hr.employee","Member")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    duration = fields.Integer("Duration")
    is_subtask = fields.Boolean("Sub-task?", default="True")

    # allow_subtasks