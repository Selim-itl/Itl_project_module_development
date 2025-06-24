from odoo import fields, models, api

class LeaderDesignation(models.Model):
    _name = 'project.leader.designation'
    _description = 'Store which designations are allowed for project leader role.'
    _rec_name = 'job_id'

    job_id = fields.Many2one(
        'hr.job',
        string="Allowed Job Position",
        required=True
    )

class CoordinatorDesignation(models.Model):
    _name = 'project.coordinator.designation'
    _description = 'Store which designations are allowed for project coordinator role.'
    _rec_name = 'job_id'

    job_id = fields.Many2one(
        'hr.job',
        string="Allowed Job Position",
        required=True
    )


