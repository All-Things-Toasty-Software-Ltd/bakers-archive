# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

{
    'name': "Baker's Archive",
    'category': 'Toasty Software',
    'sequence': 200,
    'website': 'https://www.toastysoftware.co.uk',
    'summary': "Archive of all things baking (mostly just recipes though).",
    'version': '0.4.9',
    'depends': ['website_mail', 'website_partner', 'html_builder'],

    'currency': 'EUR',
    'price': 0.00,
    'description': """
Baker's Archive
===============

The Baker's Archive consists of the data models and class structure to handle the basic creation and managing
of recipes and archive data as well as displaying them on an Odoo website.
    """,
    'data': [
        'data/mail_message_subtype_data.xml',
        'data/mail_templates.xml',
        'data/bakers_archive_data.xml',
        'data/archive_snippet_template_data.xml',
        'data/bakers_archive_tour.xml',

        'views/partner_views.xml',
        'views/bakers_archive_archive_views.xml',
        'views/bakers_archive_recipe_views.xml',
        'views/bakers_archive_tag_category_views.xml',
        'views/bakers_archive_tag_views.xml',
        'views/bakers_archive_menu_views.xml',

        'views/bakers_archive_components.xml',
        'views/bakers_archive_recipes_loop.xml',
        'views/bakers_archive_templates.xml',

        'views/snippets/snippets.xml',
        'views/snippets/s_archive_recipes.xml',
        'views/snippets/s_dynamic_snippet_archive_recipes_preview_data.xml',

        'views/bakers_archive_recipe_add.xml',

        'security/bakers_archive_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'data/bakers_archive_demo.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'bakers_archive/static/src/tours/bakers_archive.js',
        ],
        'web.assets_frontend': [
            'bakers_archive/static/src/interactions/**/*',
            'bakers_archive/static/src/scss/bakers_archive.scss',
            'bakers_archive/static/src/snippets/**/*.js',
        ],
        'website.assets_editor': [
            'bakers_archive/static/src/js/systray_items/*.js',
        ],
        'website.website_builder_assets': [
            'bakers_archive/static/src/website_builder/**/*',
        ],
    },
    'author': 'All Things Toasty Software Ltd',
    'license': 'LGPL-3',
}
