# -*- coding: utf-8 -*-

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
    _order = 'id'

    is_subtask = fields.Boolean("Is sub-task?", default="False")
    subtask_status = fields.Selection([
        ('0', 'In Progress'),
        ('100', 'Completed')
    ], string="Status", compute='_compute_subtask_status', inverse='_inverse_subtask_status', store=True, recursive=True)

    ancestor_progress_ratio = fields.Float(
        string="Progress (%)",
        compute='_compute_progress_ratio',
        store=False
    )

    @api.depends('child_ids.subtask_status')
    def _compute_subtask_status(self):
        for task in self:
            if task.child_ids:
                total = len(task.child_ids)
                done = len(task.child_ids.filtered(lambda c: c.subtask_status == '100'))
                task.subtask_status = '100' if done == total else '0'
            # Do NOT auto-change if it's a sub-task (let user control it manually)

    def _inverse_subtask_status(self):
        # Let user manually change status for leaf tasks
        pass

    @api.depends('child_ids.subtask_status', 'subtask_status')
    def _compute_progress_ratio(self):
        for task in self:
            if task.child_ids:
                total = len(task.child_ids)
                done = len(task.child_ids.filtered(lambda c: c.subtask_status == '100'))
                task.ancestor_progress_ratio = (done / total) * 100.0
            else:
                task.ancestor_progress_ratio = 100.0 if task.subtask_status == '100' else 0.0
