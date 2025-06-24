from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProjectKPI(models.Model):
    _name = "project.kpi"
    _description = "ITL Project KPI"

    # This module id been used to manage kpi related data
    name = fields.Char("KPI Name", required=True)
    target_kpi = fields.Float("Target KPI (%)", default=1)
    before_kpi = fields.Float("Before KPI (%)", default=1)
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
    achievement_percent = fields.Integer("Achievement (%)", compute="_count_achievement_percent")

    kpi_month_number = fields.Integer(
        string="Months with KPI > 0", compute="_compute_kpi_month_number", store=True
    )

    """This method count how money month does have kpi value."""
    @api.depends(
        'kpi_january', 'kpi_february', 'kpi_march', 'kpi_april', 'kpi_may', 'kpi_june',
        'kpi_july', 'kpi_august', 'kpi_september', 'kpi_october', 'kpi_november', 'kpi_december'
    )
    def _compute_kpi_month_number(self):
        for record in self:
            months = [
                record.kpi_january, record.kpi_february, record.kpi_march,
                record.kpi_april, record.kpi_may, record.kpi_june,
                record.kpi_july, record.kpi_august, record.kpi_september,
                record.kpi_october, record.kpi_november, record.kpi_december
            ]
            record.kpi_month_number = sum(1 for val in months if val > 0)

    # Calculate total achievement
    @api.depends(
        'kpi_january', 'kpi_february', 'kpi_march', 'kpi_april', 'kpi_may', 'kpi_june',
        'kpi_july', 'kpi_august', 'kpi_september', 'kpi_october', 'kpi_november', 'kpi_december',
        'kpi_month_number', 'target_kpi'
    )
    def _count_achievement(self):
        for rec in self:
            months = [
                rec.kpi_january, rec.kpi_february, rec.kpi_march, rec.kpi_april,
                rec.kpi_may, rec.kpi_june, rec.kpi_july, rec.kpi_august,
                rec.kpi_september, rec.kpi_october, rec.kpi_november, rec.kpi_december
            ]
            kpi_sum = sum(months)
            kpi_count = rec.kpi_month_number or 1  # fallback to 1 to avoid division by zero

            avg_kpi = kpi_sum / kpi_count
            target = rec.target_kpi or 1  # avoid division by zero
            rec.total_achievement = avg_kpi / target

    # Calculate achievement percentage
    @api.depends('kpi_january', 'kpi_february', 'kpi_march', 'kpi_april', 'kpi_may', 'kpi_june', 'kpi_july',
                 'kpi_august', 'kpi_september', 'kpi_october', 'kpi_november', 'kpi_december')
    def _count_achievement_percent(self):
        for rec in self:
            rec.achievement_percent = rec.total_achievement*100

    #validation for input values
    @api.constrains('target_kpi', 'before_kpi', 'kpi_january', 'kpi_february', 'kpi_march', 'kpi_april', 'kpi_may', 'kpi_june', 'kpi_july', 'kpi_august', 'kpi_september', 'kpi_october', 'kpi_november', 'kpi_december')
    def _validating_inputs(self):
        for record in self:
            if not (1 <= record.target_kpi <= 100):
                raise ValidationError(_("Target KPI value must be between 1 and 100"))
            if not (1 <= record.before_kpi <= 100):
                raise ValidationError(_("Before KPI value must be between 1 and 100"))
            if not (0 <= record.kpi_january <= 100):
                raise ValidationError(_("January KPI value must be between 0 and 100"))
            if not (0 <= record.kpi_february <= 100):
                raise ValidationError(_("February KPI value must be between 0 and 100"))
            if not (0 <= record.kpi_march <= 100):
                raise ValidationError(_("March KPI value must be between 0 and 100"))
            if not (0 <= record.kpi_april <= 100):
                raise ValidationError(_("April KPI value must be between 0 and 100"))
            if not (0 <= record.kpi_may <= 100):
                raise ValidationError(_("May KPI value must be between 0 and 100"))
            if not (0 <= record.kpi_june <= 100):
                raise ValidationError(_("June KPI value must be between 0 and 100"))
            if not (0 <= record.kpi_july <= 100):
                raise ValidationError(_("July KPI value must be between 0 and 100"))
            if not (0 <= record.kpi_august <= 100):
                raise ValidationError(_("August KPI value must be between 0 and 100"))
            if not (0 <= record.kpi_september <= 100):
                raise ValidationError(_("September KPI value must be between 0 and 100"))
            if not (0 <= record.kpi_october <= 100):
                raise ValidationError(_("October KPI value must be between 0 and 100"))
            if not (0 <= record.kpi_november <= 100):
                raise ValidationError(_("November KPI value must be between 0 and 100"))
            if not (0 <= record.kpi_december <= 100):
                raise ValidationError(_("December KPI value must be between 0 and 100"))