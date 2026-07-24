{
    'name': "Baker's Archive Core",
    'version': '0.1.0',
    'category': 'Toasty Software',
    'summary': "Core recipe and baking archive models.",
    'currency': 'EUR',
    'price': 0.00,
    'description': """
Baker's Archive Core
====================

The Baker's Archive Core consists of the core data models and class structure to handle the basic creation and managing
of recipes and archive data.
    """,
    'website': 'https://www.toastysoftware.co.uk',
    'depends': ['base',],
    'data': [
        'security/ir.model.access.csv',

        'views/bakers_archive_core_author_views.xml',
        'views/bakers_archive_core_ingredient_views.xml',
        'views/bakers_archive_core_language_views.xml',
        'views/bakers_archive_core_license_views.xml',
        'views/bakers_archive_core_origin_views.xml',
        'views/bakers_archive_core_recipe_ingredient_views.xml',
        'views/bakers_archive_core_recipe_instruction_views.xml',
        'views/bakers_archive_core_recipe_views.xml',
        'views/bakers_archive_core_source_views.xml',
        'views/bakers_archive_core_tag_views.xml',

        'views/bakers_archive_core_menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'assets': {},
    'images': [],
    'author': 'All Things Toasty Software Ltd',
    'maintainer': 'All Things Toasty Software Ltd',
    'license': 'OPL-1',
}