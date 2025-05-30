# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import timedelta


class ProjectProject(models.Model):
    _inherit = 'project.project'
    _description = 'Project project'

    allow_timesheets = fields.Boolean(default=False)

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

    # #providing button to kanban for open project settings
    # def action_open_form_view(self):
    #     self.ensure_one()  # Ensure only one record is processed
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'project.project',
    #         'res_id': self.id,
    #         'view_mode': 'form',
    #         'target': 'self',
    #     }

class ProjectTask(models.Model):
    _inherit = 'project.task'
    _order = 'sequence, id'

    task_start_date = fields.Date(string='Start date')

    # Works with stage calculation
    # task_stages = fields.Selection([
    #     ('not_started', 'Not started'),
    #     ('in_progress', 'In progress'),
    #     ('completed', 'Completed'),
    #     ('cancelled', 'Cancelled'),
    #     ('hold', 'Hold')], compute="_check_and_change_stage",default='not_started', string="Stage", tracking=True)

    task_stages = fields.Selection([
        ('not_started', 'Not started'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('hold', 'Hold')], default='not_started', string="Stage", tracking=True)

    sub_task_progress = fields.Integer("Sub-task progress (%)", group_operator=False, default=0,help="Value must be between 0 and 100")

    task_progress = fields.Integer(
        string="Task (%)",
        compute='_onchange_task_progress',
        # group_operator=False
    )

    working_days = fields.Integer(string='Allocated Days', compute='_compute_working_days', store=True)

    #Check progress value and change stage if progress is 100
    # @api.depends('sub_task_progress')
    # def _check_and_change_stage(self):
    #     for rec in self:
    #         if rec.parent_id:
    #             if rec.sub_task_progress == 100:
    #                 rec.task_stages = 'completed'
    #             elif rec.sub_task_progress == 0:
    #                 rec.task_stages = 'not_started'
    #             else:
    #                 rec.task_stages = 'in_progress'
    #         else:
    #             if rec.task_progress == 100:
    #                 rec.task_stages = 'completed'
    #             elif rec.task_progress == 0:
    #                 rec.task_stages = 'not_started'
    #             else:
    #                 rec.task_stages = 'in_progress'

    #restrict parent task deletion before deleting its sub task/tasks
    def unlink(self):
        for task in self:
            if task.child_ids:
                raise ValidationError(_("You cannot delete a parent task that has child tasks. Please delete its child tasks first."))
        return super(ProjectTask, self).unlink()

    #setting value to task and sub-task progress based on states
    @api.onchange('task_stages')
    def _stage_based_progress(self):
        for rec in self:
            if rec.task_stages == "not_started":
                rec.sub_task_progress = 0
                if not rec.parent_id:
                    rec.task_progress = 0
            if rec.task_stages in ["completed","cancelled"]:
                rec.sub_task_progress = 100
                if not rec.parent_id:
                    rec.task_progress = 100

    #validating user input to accept number between 0 and 100
    @api.constrains('sub_task_progress')
    def _check_sub_task_progress_range(self):
        for record in self:
            if not (0 <= record.sub_task_progress <= 100):
                raise ValidationError("Progress must be between 0 and 100")

    # Ensuring sub-task member who are in parent task (creating time)
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('parent_id') and vals.get('user_ids'):
                parent_users = self.browse(vals['parent_id']).user_ids.ids
                for user_id in vals['user_ids'][0][2]:  # M2M '[(6, 0, [ids])]
                    if user_id not in parent_users:
                        raise ValidationError("Sub-task assignees must be selected from parent task's assignees.")
        return super().create(vals_list)


    # Ensuring sub task member who are in parent task (editing time)
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

                # Collect child stages
                child_stages = [child.task_stages for child in task.child_ids]
                non_cancelled_stages = [s for s in child_stages if s != 'cancelled']

                if all(s == 'completed' for s in child_stages):
                    task.task_stages = 'completed'
                elif all(s == 'not_started' for s in child_stages):
                    task.task_stages = 'not_started'
                elif all(s == 'hold' for s in child_stages):
                    task.task_stages = 'hold'
                elif all(s == 'cancelled' for s in child_stages):
                    task.task_stages = 'cancelled'
                elif non_cancelled_stages:
                    if all(s == 'completed' for s in non_cancelled_stages):
                        task.task_stages = 'completed'
                    elif all(s == 'not_started' for s in non_cancelled_stages):
                        task.task_stages = 'not_started'
                    elif all(s == 'hold' for s in non_cancelled_stages):
                        task.task_stages = 'hold'
                    else:
                        task.task_stages = 'in_progress'
                else:
                    task.task_stages = 'cancelled'  # fallback if all were cancelled
            else:
                # No child tasks — manual stage control or default
                task.task_progress = 0.0
                # if task.task_stages not in ('completed', 'cancelled'):
                #     task.task_stages = 'not_started'


                # progresses = [child.task_stages for child in task.child_ids]
                # if all(p == "completed" for p in progresses):
                #     task.task_stages = 'completed'
                # elif all(p == "not_started" for p in progresses):
                #     task.task_stages = 'not_started'
                # elif all(p == "cancelled" for p in progresses):
                #     task.task_stages = 'cancelled'
                # elif all(p == "hold" for p in progresses):
                #     task.task_stages = 'hold'
                # elif any(p in ["hold","not_started","in_progress"] for p in progresses):
                #     task.task_stages = 'in_progress'
                # else:
                #     task.task_stages = 'not_started'

                # Update task_stages
                # progresses = [child.sub_task_progress for child in task.child_ids]
                # if all(p == 100 for p in progresses):
                #     task.task_stages = 'completed'
                # elif any(p > 0 for p in progresses):
                #     task.task_stages = 'in_progress'
                # else:
                #     task.task_stages = 'not_started'
            # else:
            #     task.task_progress = 0.0
