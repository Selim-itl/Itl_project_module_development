from odoo import fields, models

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