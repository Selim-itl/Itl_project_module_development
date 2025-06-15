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
    total_achievement = fields.Float("Total Achievement", compute="_count_achievement")
    achievement_percent = fields.Integer("Achievement (%)")

    @api.depends('kpi_january', 'kpi_february', 'kpi_march', 'kpi_april', 'kpi_may', 'kpi_june','kpi_july', 'kpi_august', 'kpi_september', 'kpi_october', 'kpi_november','kpi_december')
    def _count_achievement(self):
        for rec in self:
            rec.total_achievement = rec.kpi_january + rec.kpi_february + rec.kpi_march + rec.kpi_april + rec.kpi_may + rec.kpi_june + rec.kpi_july + rec.kpi_august + rec.kpi_september + rec.kpi_october + rec.kpi_november + rec.kpi_december
