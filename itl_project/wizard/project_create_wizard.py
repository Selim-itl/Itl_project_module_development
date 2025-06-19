from odoo import models


class ProjectCreateInherit(models.TransientModel):
    _inherit = 'project.create.project'

    def action_create_project(self):
        res = super().action_create_project()

        # Find the newly created project
        project_id = self.env['project.project'].search([], order='id desc', limit=1).id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Project',
            'res_model': 'project.project',
            'res_id': project_id,
            'view_mode': 'form',
            'target': 'current',
        }
