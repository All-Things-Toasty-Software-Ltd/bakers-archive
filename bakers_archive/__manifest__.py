{
    'name': "Baker's Archive",
    'version': '0.2.0',
    'category': 'Toasty Software',
    'summary': "Archive of all things baking (mostly just recipes though).",
    'currency': 'EUR',
    'price': 0.00,
    'description': """
Baker's Archive
===============

The Baker's Archive consists of the data models and class structure to handle the basic creation and managing
of recipes and archive data as well as displaying them on an Odoo website.
    """,
    'website': 'https://www.toastysoftware.co.uk',
    'depends': ['website_mail', 'website_partner', 'html_builder'],
    'data': [
        'securty/bakers_archive_security.xml'
        'security/ir.model.access.csv',

        'views/bakers_archive_archive_views.xml',
        'views/bakers_archive_author_views.xml',
        'views/bakers_archive_ingredient_views.xml',
        'views/bakers_archive_language_views.xml',
        'views/bakers_archive_license_views.xml',
        'views/bakers_archive_origin_views.xml',
        'views/bakers_archive_recipe_add_views.xml',
        'views/bakers_archive_recipe_ingredient_views.xml',
        'views/bakers_archive_recipe_instruction_views.xml',
        'views/bakers_archive_recipe_views.xml',
        'views/bakers_archive_source_views.xml',
        'views/bakers_archive_tag_category_views.xml',
        'views/bakers_archive_tag_views.xml',

        'views/bakers_archive_menu_views.xml',
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