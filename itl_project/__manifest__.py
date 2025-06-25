{
    'name': "Itl project",
    'author': "Itl",
    'category': 'Project Management',
    'version': '16.0.0',
    'depends': ['base', 'project', 'sale_project', 'hr_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_project_inherit.xml',
        'views/project_task_inherit_view.xml',
        'views/hr_timesheet_inherit_view.xml',
        'views/project_project_view.xml',
        'views/Project_KPI_views.xml',
        'views/project_3w_view.xml',
        'views/project_attendance_view.xml',
        'views/project_attendance_report_line_view.xml',
    ],
    'images': [
        'static/description/app-banner.jpg'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
