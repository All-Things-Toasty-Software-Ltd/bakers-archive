from odoo import fields, models

class BakersArchiveCoreIngredient(models.Model):
    _name = 'bakers_archive.core.ingredient'
    _description = 'Bakers Archive Core Ingredient'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')
    recipe_ingredient_id = fields.One2many('bakers_archive.core.recipe.ingredient', 'ingredient', string='Recipe Ingredient')