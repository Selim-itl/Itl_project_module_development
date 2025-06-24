from odoo import fields, models, api

class LeaderDesignation(models.Model):
    _name = 'project.leader.designation'
    _description = 'Store which designations are allowed for project leader role.'

    fields = models.Char(string="Designation Title")

class CoordinatorDesignation(models.Model):
    _name = 'project.coordinator.designation'
    _description = 'Store which designations are allowed for project coordinator role.'

    fields = models.Char(string="Designation Title")


