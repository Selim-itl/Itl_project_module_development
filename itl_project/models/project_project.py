# -*- coding: utf-8 -*-
from email.policy import default

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)

class ProjectProject(models.Model):
    _inherit = 'project.project'
    _description = 'Project project'

    allow_timesheets = fields.Boolean(default=False)
    project_progress = fields.Integer(
        string="Project Progress",
        compute="_compute_project_progress",
        help="Average progress of all tasks in this project.",
    )
    days_count = fields.Integer("Working Days", compute="_compute_working_days_duration", store=True, help="Duration in working days (excluding Fridays)")
    completed_task = fields.Integer("Completed Task", compute='_compute_completed_tasks', store=True)
    in_progress_task = fields.Integer("In-progress Task", compute="_compute_inprogress_tasks", store=True)
    not_started_task = fields.Integer("Not started Task", compute="_compute_not_started_tasks", store=True)

    project_stages = fields.Selection([
        ('not_started', 'Not started'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed')], default='not_started', string="Status", compute="_compute_project_stages")
    project_sponsor = fields.Many2one(
        "res.partner",
        string="Sponsor"
    )

    #########

    # Project Leader (senior employees only)
    project_leader_id = fields.Many2one(
        'hr.employee',
        string='Project Leader',
        domain="[('job_id.name', 'in', ['Chief Executive Officer', 'Chief Operating Officer', 'Regional Managing Director', 'HR Manager', 'HoD Accounts', 'HoD IT', 'HoD Finance', 'HoD CS', 'HoD Dispatch', 'HoD Sales & Marketing'])]",
        help='Only senior employees can be assigned as project leader.'
    )

    # Project Coordinator (senior employees only)
    project_coordinator = fields.Many2one(
        'hr.employee',
        string='Project Coordinator',
        domain="[('job_id.name', 'in', ['Chief Executive Officer', 'Chief Operating Officer', 'Regional Managing Director', 'HR Manager', 'HoD Accounts', 'HoD IT', 'HoD Finance', 'HoD CS', 'HoD Dispatch', 'HoD Sales & Marketing'])]",
        help='Only senior employees can be assigned as project coordinator.'
    )

    # Project Members (any employee allowed)
    assigned_members = fields.Many2many(
        'hr.employee',
        'project_project_member_rel',
        'project_id',
        'employee_id',
        string='Project Members',
        help='Any employee can be a project member.'
    )

    # Optional computed user fields for use in access rules
    leader_user_id = fields.Many2one(
        'res.users',
        compute='_compute_user_links',
        store=False
    )
    coordinator_user_id = fields.Many2one(
        'res.users',
        compute='_compute_user_links',
        store=False
    )
    member_user_ids = fields.Many2many(
        'res.users',
        compute='_compute_user_links',
        store=False,
        string="Member Users"
    )

    @api.depends('project_leader_id', 'project_coordinator', 'assigned_members')
    def _compute_user_links(self):
        for rec in self:
            rec.leader_user_id = rec.project_leader_id.user_id if rec.project_leader_id else False
            rec.coordinator_user_id = rec.project_coordinator.user_id if rec.project_coordinator else False
            rec.member_user_ids = rec.assigned_members.mapped('user_id')

    # Constraint to restrict leader/coordinator by job title
    @api.constrains('project_leader_id', 'project_coordinator')
    def _check_project_roles(self):
        allowed_positions = [
            'Chief Executive Officer', 'Chief Operating Officer', 'Regional Managing Director',
            'HR Manager', 'HoD Accounts', 'HoD IT', 'HoD Finance',
            'HoD CS', 'HoD Dispatch', 'HoD Sales & Marketing'
        ]
        for rec in self:
            for emp, role in [
                (rec.project_leader_id, 'leader'),
                (rec.project_coordinator, 'coordinator')
            ]:
                if emp and emp.job_id.name not in allowed_positions:
                    raise ValidationError(
                        f"{emp.name} cannot be assigned as project {role} due to their job position."
                    )

    #########


    # Method to open KPI form and tree views
    def action_view_kpi(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'KPI',
            'res_model': 'project.kpi',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],  # Optional if KPIs are per project
            'context': {
                'default_project_id': self.id
            },
        }

    # Method to open 3W form and tree views
    def action_view_3w(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': '3W',
            'res_model': 'project.three.w',
            'view_mode': 'tree,form',
            'domain': [('project_id', '=', self.id)],  # Optional if KPIs are per project
            'context': {
                'default_project_id': self.id
            },
        }

    #Display all task and sub-task of current project
    def action_stat_button_all_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'All Tasks',
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'domain': [
                ('project_id', '=', self.id)
            ],
            'context': {
                'default_project_id': self.id
            },
        }

    # Method to open all parent tasks
    def action_stat_button_parent_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parent Tasks',
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'domain': [
                ('project_id', '=', self.id),
                ('parent_id', '=', False)
            ],
            'context': {
                'default_project_id': self.id
            },
        }

    # Method to open attendance sheet
    def action_stat_button_attendance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance',
            'res_model': 'project.attendance.sheet',
            'view_mode': 'tree,form',
            'domain': [
                ('project_id', '=', self.id)
            ],
            'context': {
                'default_project_id': self.id
            },
        }

    """Method to open attendance report tree view"""
    def action_view_attendance_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance Report',
            'res_model': 'project.attendance.report.line',
            'view_mode': 'tree',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id, 'search_default_group_by_date': 1},
        }



    # Method to prevent error when clicking dummy stat button
    def action_stat_button_method(self):
        for rec in self:
            print("Method executed successfully!")

    #compute project stages
    @api.depends('task_ids.task_stages')
    def _compute_project_stages(self):
        for rec in self:
            tasks = rec.task_ids
            stages = [task.task_stages for task in tasks]

            if all(s == "completed" for s in stages):
                rec.project_stages = "completed"
            elif all(s == "not_started" for s in stages):
                rec.project_stages = "not_started"
            else:
                rec.project_stages = "in_progress"

    #compute not started tasks number
    @api.depends('task_ids.task_stages')
    def _compute_not_started_tasks(self):
        for rec in self:
            rec.not_started_task = len(rec.task_ids.filtered(lambda task: task.task_stages == "not_started"))

    #compute in-progress tasks number
    @api.depends('task_ids.task_stages')
    def _compute_inprogress_tasks(self):
        for rec in self:
            rec.in_progress_task = len(rec.task_ids.filtered(lambda task: task.task_stages == "in_progress"))

    #completed tasks count
    @api.depends('task_ids.task_stages')
    def _compute_completed_tasks(self):
        for project in self:
            project.completed_task = len(project.task_ids.filtered(lambda task: task.task_stages == 'completed'))


    #counting working days
    @api.depends('date_start', 'date')
    def _compute_working_days_duration(self):
        for project in self:
            if project.date_start and project.date:
                delta = project.date - project.date_start
                if delta.days < 0:
                    project.days_count = 0
                    continue

                total_days = delta.days + 1  # inclusive of both start and end dates
                current_date = project.date_start
                working_days = 0

                for day in range(total_days):
                    if current_date.weekday() != 4:  # 4 = Friday
                        working_days += 1
                    current_date += timedelta(days=1)

                project.days_count = working_days
            else:
                project.days_count = 0

    #calculating project progress
    @api.depends('task_ids.task_progress')
    def _compute_project_progress(self):
        for project in self:
            top_tasks = project.task_ids.filtered(lambda t: not t.parent_id and t.task_progress is not None)
            total = sum(t.task_progress for t in top_tasks)
            count = len(top_tasks)
            project.project_progress = round(total / count, 2) if count else 0.0

    # #providing button to kanban for open project settings. This is getting triggered by clicking on project display name.
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
    _order = 'sequence, id'

    task_start_date = fields.Date(string='Start date')
    user_ids = fields.Many2many(string='Assigned To')
    # Works with stage calculation
    task_stages = fields.Selection([
        ('not_started', 'Not started'),
        ('in_progress', 'In progress'),
        ('completed', 'Completed')], compute="_check_and_change_stage",default='not_started', string="Stage", tracking=True)

    sub_task_progress = fields.Integer("Sub-task progress (%)", group_operator=False, default=0,help="Value must be between 0 and 100")

    task_progress = fields.Integer(
        string="Task (%)",
        compute='_onchange_task_progress',
        # group_operator=False
    )

    working_days = fields.Integer(string='Allocated Days', compute='_compute_working_days', store=True)

    allowed_user_ids = fields.Many2many(
        'res.users',
        compute='_compute_allowed_user_ids',
        store=False
    )

    #Ensures only project members are appears in task assign to form.
    @api.depends('project_id', 'parent_id')
    def _compute_allowed_user_ids(self):
        for task in self:
            if task.project_id and not task.parent_id:
                # Get all employees (members, leader, coordinator)
                employees = task.project_id.assigned_members \
                            | task.project_id.project_coordinator \
                            | task.project_id.project_leader_id

                # Filter those who have a user_id and map to users
                task.allowed_user_ids = employees.mapped('user_id').filtered(lambda u: u)
            else:
                task.allowed_user_ids = self.env['res.users']

    # Check progress value and change stage if progress is 100
    @api.depends('sub_task_progress')
    def _check_and_change_stage(self):
        for rec in self:
            if rec.parent_id:
                if rec.sub_task_progress == 100:
                    rec.task_stages = 'completed'
                elif rec.sub_task_progress == 0:
                    rec.task_stages = 'not_started'
                else:
                    rec.task_stages = 'in_progress'
            else:
                if rec.task_progress == 100:
                    rec.task_stages = 'completed'
                elif rec.task_progress == 0:
                    rec.task_stages = 'not_started'
                else:
                    rec.task_stages = 'in_progress'

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

                progresses = [child.sub_task_progress for child in task.child_ids]
                if all(p == 100 for p in progresses):
                    task.task_stages = 'completed'
                elif any(p > 0 for p in progresses):
                    task.task_stages = 'in_progress'
                else:
                    task.task_stages = 'not_started'
            else:
                task.task_progress = 0.0