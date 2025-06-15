from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

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
    total_achievement = fields.Float("Total Achievement", compute="_count_achievement", store=True)
    achievement_percent = fields.Integer("Achievement", compute="_count_achievement_percent")

    # Calculate total achievement
    @api.depends('kpi_january', 'kpi_february', 'kpi_march', 'kpi_april', 'kpi_may', 'kpi_june', 'kpi_july',
                 'kpi_august', 'kpi_september', 'kpi_october', 'kpi_november', 'kpi_december')
    def _count_achievement(self):
        for rec in self:
            rec.total_achievement = rec.kpi_january + rec.kpi_february + rec.kpi_march + rec.kpi_april + rec.kpi_may + rec.kpi_june + rec.kpi_july + rec.kpi_august + rec.kpi_september + rec.kpi_october + rec.kpi_november + rec.kpi_december

    # Calculate achievement percentage
    @api.depends('kpi_january', 'kpi_february', 'kpi_march', 'kpi_april', 'kpi_may', 'kpi_june', 'kpi_july',
                 'kpi_august', 'kpi_september', 'kpi_october', 'kpi_november', 'kpi_december')
    def _count_achievement_percent(self):
        for rec in self:
            rec.achievement_percent = (100/1200)*rec.total_achievement

    #validation for input values
    @api.constrains('target_kpi', 'before_kpi', 'kpi_january', 'kpi_february', 'kpi_march', 'kpi_april', 'kpi_may', 'kpi_june', 'kpi_july', 'kpi_august', 'kpi_september', 'kpi_october', 'kpi_november', 'kpi_december')
    def _validating_inputs(self):
        for record in self:
            if not (0 <= record.target_kpi <= 100):
                raise ValidationError("Target KPI value must be between 0 and 100")
            if not (0 <= record.before_kpi <= 100):
                raise ValidationError("Before KPI value must be between 0 and 100")
            if not (0 <= record.kpi_january <= 100):
                raise ValidationError("January KPI value must be between 0 and 100")
            if not (0 <= record.kpi_february <= 100):
                raise ValidationError("February KPI value must be between 0 and 100")
            if not (0 <= record.kpi_march <= 100):
                raise ValidationError("March KPI value must be between 0 and 100")
            if not (0 <= record.kpi_april <= 100):
                raise ValidationError("April KPI value must be between 0 and 100")
            if not (0 <= record.kpi_may <= 100):
                raise ValidationError("May KPI value must be between 0 and 100")
            if not (0 <= record.kpi_june <= 100):
                raise ValidationError("June KPI value must be between 0 and 100")
            if not (0 <= record.kpi_july <= 100):
                raise ValidationError("July KPI value must be between 0 and 100")
            if not (0 <= record.kpi_august <= 100):
                raise ValidationError("August KPI value must be between 0 and 100")
            if not (0 <= record.kpi_september <= 100):
                raise ValidationError("September KPI value must be between 0 and 100")
            if not (0 <= record.kpi_october <= 100):
                raise ValidationError("October KPI value must be between 0 and 100")
            if not (0 <= record.kpi_november <= 100):
                raise ValidationError("November KPI value must be between 0 and 100")
            if not (0 <= record.kpi_december <= 100):
                raise ValidationError("December KPI value must be between 0 and 100")