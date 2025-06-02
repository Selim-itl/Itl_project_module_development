from odoo import api, fields, models

class ProjectKPI(models.Model):
    _name = "project.kpi"
    _description = "ITL Project KPI"

    name = fields.Char("KPI Name")
    target_kpi = fields.Float("Target KPI")
    before_kpi = fields.Float("Before KPI")
    current_month = fields.Integer("Current Month")
    achievement = fields.Float("Achievement")
    remarks = fields.Char("Remarks")
    project_id = fields.Many2one("project.project", "Project")