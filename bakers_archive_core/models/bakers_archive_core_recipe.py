from odoo import fields, models


class BakersArchiveCoreRecipe(models.Model):
    _name = 'bakers_archive.core.recipe'
    _description = 'Bakers Archive Core Recipe'


    active = fields.Boolean(default=True)

    # Metadata

    name = fields.Char(string='Recipe Name', tracking=True)
    author = fields.Char(string='Author')
    license = fields.Char(string='License')
    language = fields.Char(string='Language')
    origin = fields.Char(string='Origin')
    tags = fields.Char(string='Tags')

    # Recipe

    description = fields.Char(string='Description')
    ingredients = fields.One2many('bakers_archive.core.recipe.ingredient', 'recipe_id', string='Ingredients')
    instructions = fields.Char(string='Instructions')
    notes = fields.Char(string='Notes')

