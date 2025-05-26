# -*- coding: utf-8 -*-
{
    "name": "OM Hospital",
    "version": "1.0",
    "category": "Tests",
    "description": """A module to test the Group functionality.""",
    "depends": ["base"],
    "installable": True,
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/root_menu_view.xml',
        'views/doctor_view.xml',
        'views/patient_view.xml',
        'views/appointment_view.xml',
        'views/tags_view.xml',
        'views/room_view.xml',
    ],
    'license': 'LGPL-3',
    "application": True,
}