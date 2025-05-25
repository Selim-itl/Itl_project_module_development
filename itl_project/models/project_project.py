#Updated code written at the morning of 25 May 8:00 AM
# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields, api
from datetime import timedelta

class ProjectProject(models.Model):
    _inherit = 'project.project'
    _description = 'Project project'

    project_progress = fields.Integer(
        string="Project Progress",
        compute="_compute_project_progress",
        help="Average progress of all tasks in this project.",
    )

    @api.depends('task_ids.task_progress')
    def _compute_project_progress(self):
        for project in self:
            top_tasks = project.task_ids.filtered(lambda t: not t.parent_id and t.task_progress is not None)
            total = sum(t.task_progress for t in top_tasks)
            count = len(top_tasks)
            project.project_progress = round(total / count, 2) if count else 0.0

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
        ('completed', 'Done')], default='not_started')

    sub_task_progress = fields.Integer("Sub-task progress (%)", group_operator=False, default=0)

    task_progress = fields.Integer(
        string="Task Progress (%)",
        compute='_onchange_task_progress',
        # group_operator=False
    )

    working_days = fields.Integer(string='Allocated Days', compute='_compute_working_days', store=True)

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
