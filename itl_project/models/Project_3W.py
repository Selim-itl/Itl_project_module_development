from odoo import fields, models, api
from odoo.exceptions import AccessError

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
    can_edit_fields = fields.Boolean("Can Edit Fields", compute='_compute_can_edit_fields', store=False)
    """Method is been used to calculate which boolean field for allowing administrator, leader and coordinator to manage records"""
    @api.depends('project_id')
    def _compute_can_edit_fields(self):
        for rec in self:
            user = self.env.user
            project = rec.project_id
            rec.can_edit_fields = bool(project) and (
                    user.has_group('project.group_project_manager') or
                    (project.user_id and project.user_id.id == user.id)  or
                    (project.project_coordinator and project.project_coordinator.id == user.id)
            )

    """Will get triggered automatically when project_id will be added/changed"""
    @api.onchange('project_id')
    def _onchange_project_id_update_can_edit(self):
        self._compute_can_edit_fields()

    """Setting the can_edit_fields value when the form gets loaded. It is userful in terms of loading the form for the first time. Without this block the value of that filed will always be false when the form get loaded for the first time."""
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'can_edit_fields' in fields_list and 'default_can_edit_fields' in self.env.context:
            res['can_edit_fields'] = self.env.context.get('default_can_edit_fields')
        return res
    # Block is been using for track who can edit

    # Block ensuring proper access right
    """Conditionally checking whether the user should have permissions to delete, duplicate, edit"""
    def check_user_role(self):
        for record in self:
            if not record.can_edit_fields:
                raise AccessError("You do not have permission to modify this project.")

    """Helper method to gain/revoke CRUD access from users"""
    def write(self, vals):
        self.check_user_role()
        return super().write(vals)

    """Helper method to gain/revoke CRUD access from users"""
    def unlink(self):
        self.check_user_role()
        return super().unlink()

    """Helper method to gain/revoke CRUD access from users"""
    def copy(self, default=None):
        self.check_user_role()
        return super().copy(default)

    # Block ensuring proper access right