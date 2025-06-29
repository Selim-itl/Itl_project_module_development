from email.policy import default

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError, AccessError

class ProjectAttendanceSheet(models.Model):
    _name = 'project.attendance.sheet'
    _description = 'Project Attendance Sheet'

    name = fields.Char(string="Description", compute="_compute_name", store=True)
    project_id = fields.Many2one('project.project', string="Project", required=True)
    attendance_date = fields.Date(string="Attendance Date", required=True, store=True)
    attendance_line_ids = fields.One2many('project.attendance.line', 'sheet_id', string="Attendance Lines")
    attendance_date_status = fields.Selection([
        ('normal', 'Regular day'),
        ('cancelled', 'Cancelled'),
        ('weekend', 'Weekend')
    ], string="Day's status", default='normal')

    # Block is been using for track who can edit
    can_edit_fields = fields.Boolean(
        string="Can Edit Fields",
        compute='_compute_can_edit_fields',
        store=False
    )

    """Computing weather logged in user is Administrator/Leader/Coordinator/normal user"""
    @api.depends('project_id')
    def _compute_can_edit_fields(self):
        for rec in self:
            user = self.env.user
            project = rec.project_id
            rec.can_edit_fields = bool(project) and (
                    user.has_group('project.group_project_manager') or
                    (project.user_id and project.user_id.id == user.id) or
                    (project.project_coordinator and project.project_coordinator.id == user.id)
            )

    """Will get triggered automatically when project_id will be added/changed"""
    @api.onchange('project_id')
    def _onchange_can_edit_fields(self):
        self._compute_can_edit_fields()

    """Setting the can_edit_fields value when the form gets loaded. It is userful in terms of loading the form for the first time. Without this block the value of that filed will always be false when the form get loaded for the first time."""
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'can_edit_fields' in fields_list and 'default_can_edit_fields' in self.env.context:
            res['can_edit_fields'] = self.env.context.get('default_can_edit_fields')
        return res

    # Block is been using for track who can edit

    # Block ensuring proper access right
    """Conditionally checking whether the user should have permissions to delete, duplicate, edit"""
    def check_user_role(self):
        for record in self:
            if not record.can_edit_fields:
                raise AccessError("You do not have permission to modify this project.")

    """Helper method to gain/revoke CRUD access from users"""
    def copy(self, default=None):
        self.check_user_role()
        return super().copy(default)

    # Block ensuring proper access right

    """Delete previous records of attendance report when edit attendance sheet and store updated record to attendance report."""
    """Here create access control is also implemented"""
    def write(self, vals):
        self.check_user_role()  # Permission check first
        result = super().write(vals)
        for sheet in self:
            self.env['project.attendance.report.line'].search([
                ('project_id', '=', sheet.project_id.id),
                ('attendance_date', '=', sheet.attendance_date)
            ]).unlink()

            for line in sheet.attendance_line_ids:
                self.env['project.attendance.report.line'].create_from_attendance_line(line)
        return result

    """If a attendance record got deleted on the same date all the attendance report record of the same date will also deleted from here."""
    """Here delete access control also implemented """
    def unlink(self):
        self.check_user_role()  # Permission check first
        report_line_model = self.env['project.attendance.report.line']
        for sheet in self:
            report_lines = report_line_model.search([
                ('project_id', '=', sheet.project_id.id),
                ('attendance_date', '=', sheet.attendance_date)
            ])
            report_lines.unlink()
        return super().unlink()

    """Generating title or name or description for each record based on date and project name"""
    @api.depends('project_id', 'attendance_date')
    def _compute_name(self):
        for rec in self:
            rec.name = f"Attendance for {rec.project_id.name} on {rec.attendance_date if rec.attendance_date else '0000-00-00'}"

    """This method will auto fill all assigned persons to attendance line when date will be selected. 
    It also remove line values if date is changes and re-populate line value."""
    @api.onchange('attendance_date', 'project_id')
    def _onchange_date_project(self):
        if self.attendance_date and self.project_id:
            assigned_users = (
                    self.project_id.user_id |
                    self.project_id.project_coordinator |
                    self.project_id.assigned_members
            ).sudo()

            # Clear existing lines
            self.attendance_line_ids = [(5, 0, 0)]

            # Populate new lines
            lines = []
            for user in assigned_users:
                lines.append((0, 0, {
                    'user_id': user.id,
                    # department_id and role will auto-compute
                }))

            self.attendance_line_ids = lines
        else:
            # If either date or project is cleared, remove lines
            self.attendance_line_ids = [(5, 0, 0)]

class ProjectAttendanceLine(models.Model):
    _name = 'project.attendance.line'
    _description = 'Project Attendance Line'

    sheet_id = fields.Many2one('project.attendance.sheet', string="Attendance Sheet", required=True, ondelete='cascade')
    user_id = fields.Many2one(
        'res.users',
        string="User",
        required=True
    )
    department_id = fields.Many2one('hr.department', string="Department", compute='_compute_department', store=True)
    role = fields.Selection([
        ('leader', 'Leader'),
        ('coordinator', 'Coordinator'),
        ('member', 'Member')
    ], string="Role", compute='_compute_role', store=True)
    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
        ('late', 'Late')
    ], string="Status", required=True, default="present")
    attendance_date = fields.Date(
        related='sheet_id.attendance_date',
        store=True,
        string='Date'
    )

    """Inheriting default create method to extend functionality. Now when a new attendance got recorded a record for attendance report is also get stored."""
    @api.model
    def create(self, vals):
        record = super().create(vals)
        self.env['project.attendance.report.line'].create_from_attendance_line(record)
        return record

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

    """Fetch only unique users in the result. Now only which users are not selected will get appeared in the result."""
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
                'user_id': []
            }
        }

class ProjectAttendanceReportLine(models.Model):
    _name = 'project.attendance.report.line'
    _description = 'Flattened Attendance Report'
    _rec_name = 'user_id'
    _order = 'attendance_date desc'

    project_id = fields.Many2one('project.project', string="Project", required=True)
    user_id = fields.Many2one('res.users', string="User", required=True)
    department_id = fields.Many2one('hr.department', string="Department")
    attendance_date = fields.Date(string="Date", required=True)
    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'Leave'),
        ('late', 'Late')
    ], string="Status")

    """Create attendance report record by checking existing records availability"""
    @api.model
    def create_from_attendance_line(self, attendance_line):
        existing = self.search([
            ('user_id', '=', attendance_line.user_id.id),
            ('attendance_date', '=', attendance_line.attendance_date)
        ], limit=1)

        values = {
            'user_id': attendance_line.user_id.id,
            'department_id': attendance_line.department_id.id,
            'attendance_date': attendance_line.attendance_date,
            'status': attendance_line.status,
            'project_id': attendance_line.sheet_id.project_id.id,
        }

        if existing:
            existing.write(values)
        else:
            self.create(values)