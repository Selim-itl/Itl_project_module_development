from odoo import fields, models, api

class Project3W(models.Model):
    _name = "project.three.w"
    _description = "Project 3W"

    name = fields.Char("Action Items", required=True)
    project_id = fields.Many2one("project.project", "Project")
    day_date = fields.Date("Date")
    when_date = fields.Date("When")
    responsible = fields.Many2many("res.partner", string="Responsible")
    status = fields.Selection([
        ('not_started', 'Not started'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed')], default='not_started', string="Status")

    # Block is been using for track who can edit
    can_edit_fields = fields.Boolean(compute='_compute_can_edit_fields', store=False)

    """This method is ensuring project module's Administrator, project leader and project coordinator can only edit certain field."""
    @api.depends('project_id')
    def _compute_can_edit_fields(self):
        for task in self:
            user = self.env.user
            project = task.project_id
            task.can_edit_fields = bool(project) and (
                    user.has_group('project.group_project_manager') or
                    (project.user_id and project.user_id.id == user.id) or
                    (project.project_coordinator and project.project_coordinator.id == user.id)
            )
    # Block is been using for track who can edit