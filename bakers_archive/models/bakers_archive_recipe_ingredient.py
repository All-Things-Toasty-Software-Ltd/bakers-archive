from odoo import fields, models


class BakersArchiveRecipeIngredient(models.Model):
    _name = 'bakers_archive.recipe.ingredient'
    _description = 'Bakers Archive Recipe Ingredient'

    recipe_id = fields.Many2one('bakers_archive.recipe', String="Recipe ID", ondelete='cascade')

    quantity = fields.Float(string='Quantity')
    unit = fields.Char(string='Unit')
    ingredient = fields.Many2one('bakers_archive.ingredient', string='Ingredient')
    notes = fields.Text(string='Notes')
