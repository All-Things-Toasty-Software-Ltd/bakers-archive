from odoo import fields, models


class BakersArchiveRecipe(models.Model):
    _name = 'bakers_archive.recipe'
    _description = 'Bakers Archive Recipe'

    active = fields.Boolean(default=True)

    # Metadata

    name = fields.Char(string='Recipe Name', tracking=True)
    sources = fields.Many2many('bakers_archive.source', string='Sources')
    authors = fields.Many2many('bakers_archive.author', string='Authors')
    license = fields.Many2one('bakers_archive.license', string='License')
    languages = fields.Many2many('bakers_archive.language', string='Languages')
    origins = fields.Many2many('bakers_archive.origin', string='Origins')
    tags = fields.Many2many('bakers_archive.tag', string='Tags')

    # Recipe

    description = fields.Text(string='Description')
    ingredients = fields.One2many('bakers_archive.recipe.ingredient', 'recipe_id', string='Ingredients')
    instructions = fields.One2many('bakers_archive.recipe.instruction', 'recipe_id', string='Instructions')
    notes = fields.Text(string='Notes')

    # Media

    image = fields.Image(string='Image')
