from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = "project.project"

    members = fields.Many2many("hr.employee", string="Members")
    progress = fields.Integer("Progress")
    estimated_cost = fields.Float('Estimated cost')
    actual_cost = fields.Float('Actual cost')
    days_allocated = fields.Integer("Allocated days")
    total_task = fields.Integer("Total Task")
    completed_task = fields.Integer("Completed Task")
    sub_task = fields.Integer("Sub Task")

    def btn_action(self):
        return