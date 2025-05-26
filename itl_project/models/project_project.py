# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import timedelta

class ProjectProject(models.Model):
    _inherit = 'project.project'
    _description = 'Project project'

    project_progress = fields.Integer(
        string="Project Progress",
        compute="_compute_project_progress",
        help="Average progress of all tasks in this project.",
    )

    #calculating project progress
    @api.depends('task_ids.task_progress')
    def _compute_project_progress(self):
        for project in self:
            top_tasks = project.task_ids.filtered(lambda t: not t.parent_id and t.task_progress is not None)
            total = sum(t.task_progress for t in top_tasks)
            count = len(top_tasks)
            project.project_progress = round(total / count, 2) if count else 0.0

    #providing button to kanban for open project settings
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

    task_start_date = fields.Date(string='Start date')
    task_stages = fields.Selection([
        ('not_started', 'Not started'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed')], default='not_started', string="Stage", tracking=True)

    sub_task_progress = fields.Integer("Sub-task progress (%)", group_operator=False, default=0)

    task_progress = fields.Integer(
        string="Task (%)",
        compute='_onchange_task_progress',
        # group_operator=False
    )

    working_days = fields.Integer(string='Allocated Days', compute='_compute_working_days', store=True)

    #setting users to sub-tasks by filter. Now users who are not in parent task are not visible to sub-tasks.
    # @api.onchange('parent_id')
    # def _onchange_parent_id(self):
    #     if self.parent_id:
    #         return {'domain': {'user_ids': [('id', 'in', self.parent_id.user_ids.ids)]}}
    #     else:
    #         return {'domain': {'user_ids': []}}  # or no restriction

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('parent_id') and vals.get('user_ids'):
                parent_users = self.browse(vals['parent_id']).user_ids.ids
                for user_id in vals['user_ids'][0][2]:  # M2M '[(6, 0, [ids])]
                    if user_id not in parent_users:
                        raise ValidationError("Sub-task assignees must be selected from parent task's assignees.")
        return super().create(vals_list)

    def write(self, vals):
        for task in self:
            if 'user_ids' in vals and task.parent_id:
                parent_users = task.parent_id.user_ids.ids
                for user_id in vals['user_ids'][0][2]:  # M2M write format
                    if user_id not in parent_users:
                        raise ValidationError("Sub-task assignees must be selected from parent task's assignees.")
        return super().write(vals)




    #calculating working days by excluding weekend
    @api.depends('task_start_date', 'date_deadline')
    def _compute_working_days(self):
        for task in self:
            start_date = task.task_start_date
            end_date = task.date_deadline
            if start_date and end_date and start_date <= end_date:
                current_date = start_date
                count = 0
                while current_date <= end_date:
                    # weekday() Monday=0 ... Sunday=6
                    if current_date.weekday() != 4:  # 4 is Friday
                        count += 1
                    current_date += timedelta(days=1)
                task.working_days = count
            else:
                task.working_days = 0

    #calculating task progress from sub-tasks and setting task status based on task progress
    @api.depends('child_ids.sub_task_progress')
    def _onchange_task_progress(self):
        for task in self:
            if task.child_ids:
                total = len(task.child_ids)
                total_progress = sum(child.sub_task_progress for child in task.child_ids)
                task.task_progress = round(total_progress / total, 2) if total else 0.0

                # Update task_stages
                progresses = [child.sub_task_progress for child in task.child_ids]
                if all(p == 100 for p in progresses):
                    task.task_stages = 'completed'
                elif any(p > 0 for p in progresses):
                    task.task_stages = 'in_progress'
                else:
                    task.task_stages = 'not_started'
            else:
                task.task_progress = 0.0
