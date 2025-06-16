from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class ProjectAttendanceSheet(models.Model):
    _name = 'project.attendance.sheet'
    _description = 'Project Attendance Sheet'

    name = fields.Char(string="Description", compute="_compute_name", store=True)
    project_id = fields.Many2one('project.project', string="Project", required=True)
    attendance_date = fields.Date(string="Attendance Date", required=True, default=fields.Date.context_today)
    attendance_line_ids = fields.One2many('project.attendance.line', 'sheet_id', string="Attendance Lines")

    @api.depends('project_id', 'attendance_date')
    def _compute_name(self):
        for rec in self:
            rec.name = f"Attendance for {rec.project_id.name} on {rec.attendance_date}"


class ProjectAttendanceLine(models.Model):
    _name = 'project.attendance.line'
    _description = 'Project Attendance Line'

    sheet_id = fields.Many2one('project.attendance.sheet', string="Attendance Sheet", required=True, ondelete='cascade')
    user_id = fields.Many2one(
        'res.users',
        string="User",
        required=True,
        domain="[('id', 'in', allowed_user_ids)]"
    )
    allowed_user_ids = fields.Many2many('res.users', compute='_compute_allowed_user_ids', store=False)
    department_id = fields.Many2one('hr.department', string="Department", compute='_compute_department', store=True)
    role = fields.Selection([
        ('leader', 'Leader'),
        ('coordinator', 'Coordinator'),
        ('member', 'Member')
    ], string="Role", compute='_compute_role', store=True)
    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave')
    ], string="Status", required=True)

    """Collecting only these users which are present in a certain project."""
    @api.depends('sheet_id.project_id')
    def _compute_allowed_user_ids(self):
        for rec in self:
            users = self.env['res.users']
            if rec.sheet_id.project_id:
                project = rec.sheet_id.project_id
                users = (project.user_id | project.project_coordinator | project.assigned_members).sudo()
            rec.allowed_user_ids = users

    """Getting users department if they are employee"""
    @api.depends('user_id')
    def _compute_department(self):
        for rec in self:
            employee = self.env['hr.employee'].search([('user_id', '=', rec.user_id.id)], limit=1)
            rec.department_id = employee.department_id.id if employee else False

    """Collecting users role from the project they are assigned to"""
    @api.depends('sheet_id.project_id', 'user_id')
    def _compute_role(self):
        for rec in self:
            project = rec.sheet_id.project_id
            if project:
                if rec.user_id.id == project.user_id.id:
                    rec.role = 'leader'
                elif rec.user_id.id == project.project_coordinator.id:
                    rec.role = 'coordinator'
                elif rec.user_id in project.assigned_members:
                    rec.role = 'member'
                else:
                    rec.role = False
            else:
                rec.role = False
