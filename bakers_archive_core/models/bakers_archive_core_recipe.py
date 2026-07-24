from odoo import fields, models


class BakersArchiveCoreRecipe(models.Model):
    _name = 'bakers_archive.core.recipe'
    _description = 'Bakers Archive Core Recipe'

    active = fields.Boolean(default=True)

    # Metadata

    name = fields.Char(string='Recipe Name', tracking=True)
    sources = fields.Many2many('bakers_archive.core.source', string='Sources')
    authors = fields.Many2many('bakers_archive.core.author', string='Authors')
    license = fields.Many2one('bakers_archive.core.license', string='License')
    languages = fields.Many2many('bakers_archive.core.language', string='Languages')
    origins = fields.Many2many('bakers_archive.core.origin', string='Origins')
    tags = fields.Many2many('bakers_archive.core.tag', string='Tags')

    # Recipe

    description = fields.Text(string='Description')
    ingredients = fields.One2many('bakers_archive.core.recipe.ingredient', 'recipe_id', string='Ingredients')
    instructions = fields.One2many('bakers_archive.core.recipe.instruction', 'recipe_id', string='Instructions')
    notes = fields.Text(string='Notes')
