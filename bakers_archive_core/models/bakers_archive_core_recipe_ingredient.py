from odoo import fields, models

from bakers_archive_core.models import bakers_archive_core_ingredient


class BakersArchiveCoreRecipeIngredient(models.Model):
    _name = 'bakers_archive.core.recipe.ingredient'
    _description = 'Bakers Archive Core Recipe Ingredient'

    recipe_id = fields.Many2one('bakers_archive.core.recipe', String="Recipe ID", ondelete='cascade')

    quantity = fields.Float(string='Quantity')
    unit = fields.Char(string='Unit')
    ingredient = fields.Many2one('bakers_archive.core.ingredient', string='Ingredient')
    notes = fields.Text(string='Notes')