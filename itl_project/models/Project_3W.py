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

    @api.onchange('project_id')
    def _onchange_project_id_update_can_edit(self):
        self._compute_can_edit_fields()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'can_edit_fields' in fields_list and 'default_can_edit_fields' in self.env.context:
            res['can_edit_fields'] = self.env.context.get('default_can_edit_fields')
        return res
    # Block is been using for track who can edit