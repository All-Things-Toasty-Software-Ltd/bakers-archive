from odoo import fields, models


class BakersArchiveIngredient(models.Model):
    _name = 'bakers_archive.ingredient'
    _description = 'Bakers Archive Ingredient'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')

    recipe_ingredient_id = fields.One2many('bakers_archive.recipe.ingredient', 'ingredient',
                                           string='Recipe Ingredient')
