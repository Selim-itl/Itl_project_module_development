# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields, api


class InheritCRMKanbanView(models.Model):
    _inherit = 'project.project'
    _description = 'Project project'


    def action_open_form_view(self):
        self.ensure_one()  # Ensure only one record is processed
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'self',
        }

class ProjectTask(models.Model):
    _inherit = 'project.task'
    _order = "id"

    task_stages = fields.Selection([
        ('not_started', 'Not started'),
        ('in_progress', 'In progress'),
        ('completed', 'Done')], default='not_started')

    progress_value = fields.Integer(
        string="Progress (%)",
        compute='_onchange_progress',
        store=True,
        readonly=False,  # Allows manual editing for parent tasks
        # recursive=True,
        group_operator=False
    )

# Method is got getting executed


    @api.onchange('progress_value')
    def _onchange_progress(self):
        for task in self: #Going through all tasks and sub-tasks
            if task.child_ids: #collecting only these task which are having sub-tasks
                print("Method executed")
                for sub_task in task: #Going through each of these parent tasks to get sub-tasks ids
                    # print("Sub-task ids : ", sub_task.child_ids) #Getting sub-tasks ids
                    subtask_progress = task.child_ids.mapped('progress_value')
                    valid_progress = [p for p in subtask_progress if isinstance(p, (int, float))]

                    if valid_progress:  # Only calculate if we have valid numbers
                        task.progress_value = round(sum(valid_progress) / len(valid_progress))
                        print("task.progress_value : ", task.progress_value)
                    else: #if not valid progress
                        task.progress_value = 0  # Default if no valid progress
                        print("Zero value set! ")
            else:#setting value for the tasks which are sub-tasks
                continue