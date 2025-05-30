{
    'name': "Itl project",
    'author': "Itl",
    'category': 'Project Management',
    'version': '16.0.0',
    'depends': ['base', 'project', 'sale_project', 'sale_timesheet'],
    'data': [
        'views/project_kanban_inherit.xml',
        'views/project_task_inherit_view.xml',
        'views/hr_timesheet_inherit_view.xml',
        'views/project_project_view.xml',
    ],
    'images': [
        'static/description/app-banner.jpg'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
