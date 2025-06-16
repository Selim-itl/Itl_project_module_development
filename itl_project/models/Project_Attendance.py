from odoo import models, fields, api,_
from odoo.exceptions import ValidationError

class ProjectAttendanceSheet(models.Model):
    _name = 'project.attendance.sheet'
    _description = 'Project Attendance Sheet'

    name = fields.Char(string="Description", compute="_compute_name", store=True)
    project_id = fields.Many2one('project.project', string="Project", required=True)
    attendance_date = fields.Date(string="Attendance Date", required=True)
    attendance_line_ids = fields.One2many('project.attendance.line', 'sheet_id', string="Attendance Lines")

    """Generating title or name or description for each record based on date and project name"""
    @api.depends('project_id', 'attendance_date')
    def _compute_name(self):
        for rec in self:
            rec.name = f"Attendance for {rec.project_id.name} on {rec.attendance_date if rec.attendance_date else "0000-00-00"}"


class ProjectAttendanceLine(models.Model):
    _name = 'project.attendance.line'
    _description = 'Project Attendance Line'

    sheet_id = fields.Many2one('project.attendance.sheet', string="Attendance Sheet", required=True, ondelete='cascade')
    user_id = fields.Many2one(
        'res.users',
        string="User",
        required=True
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

    """Collecting only these users which are assigned to a certain project."""
    @api.depends('sheet_id.project_id')
    def _compute_allowed_user_ids(self):
        for rec in self:
            users = self.env['res.users']
            if rec.sheet_id.project_id:
                project = rec.sheet_id.project_id
                users = (project.user_id | project.project_coordinator | project.assigned_members).sudo()
            # Joining all assigned entities and exclude duplicate with super admin permission by using sudo()
            rec.allowed_user_ids = users

    """Getting users department if they are employee else returning False"""
    @api.depends('user_id')
    def _compute_department(self):
        for rec in self:
            employee = self.env['hr.employee'].search([('user_id', '=', rec.user_id.id)], limit=1)
            rec.department_id = employee.department_id.id if employee else False
            #the department_id of employee.department_id is written in hr.employee.base model and this model is inherited by hr.employee model class.

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

    @api.onchange('sheet_id', 'user_id')
    def _onchange_user_id(self):
        if self.sheet_id and self.sheet_id.project_id:
            project = self.sheet_id.project_id
            used_user_ids = [
                line.user_id.id for line in self.sheet_id.attendance_line_ids
                if line.id != self.id and line.user_id
            ]
            assigned_user_ids = (project.user_id | project.project_coordinator | project.assigned_members).ids
            available_user_ids = list(set(assigned_user_ids) - set(used_user_ids))

            return {
                'domain': {
                    'user_id': [('id', 'in', available_user_ids)]
                }
            }

        # ⚡ Always return something, even if condition fails
        return {
            'domain': {
                'user_id': []  # or no restriction
            }
        }
