{
    'name': "Logic Base",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/logic_students.xml',
        'views/logic_batch.xml',
        'views/class_logic.xml',
        'views/stud_allocation.xml',
        'views/logic_courses.xml'

    ],
    'demo': [],
    'summary': "base_logic",
    'description': "this_is_my_app",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': True
}
