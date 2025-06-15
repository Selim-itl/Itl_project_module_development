from odoo import api, fields, models

class ProjectKPI(models.Model):
    _name = "project.kpi"
    _description = "ITL Project KPI"

    # This module id been used to manage kpi related data
    name = fields.Char("KPI Name")
    target_kpi = fields.Float("Target KPI")
    before_kpi = fields.Float("Before KPI")
    remarks = fields.Char("Remarks")
    project_id = fields.Many2one("project.project", "Project")
    kpi_january = fields.Float("January")
    kpi_february = fields.Float("February")
    kpi_march = fields.Float("March")
    kpi_april = fields.Float("April")
    kpi_may = fields.Float("May")
    kpi_june = fields.Float("June")
    kpi_july = fields.Float("July")
    kpi_august = fields.Float("August")
    kpi_september = fields.Float("September")
    kpi_october = fields.Float("October")
    kpi_november = fields.Float("November")
    kpi_december = fields.Float("December")
    additional_note = fields.Text(string='Additional Note')