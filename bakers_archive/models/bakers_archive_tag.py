from odoo import fields, models


class BakersArchiveTag(models.Model):
    _name = 'bakers_archive.tag'
    _description = 'Bakers Archive Tag'
    _inherit = ['website.seo.metadata']
    _order = 'name'

    name = fields.Char('Name', required=True, translate=True)
    category_id = fields.Many2one('bakers_archive.tag.category', 'Category', index=True)
    colour = fields.Integer('Colour', index=True)
    recipe_ids = fields.Many2many('bakers_archive.recipe', string='Recipes')

    _name_uniq = models.Constraint(
        'unique (name)',
        'Tag name already exists!',
    )
