# -*- coding: utf-8 -*-
# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BakersArchiveRecipeIngredient(models.Model):
    _name = 'bakers_archive.recipe.ingredient'
    _description = 'Bakers Archive Recipe Ingredient'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)

    quantity = fields.Float(string='Quantity')
    unit = fields.Char(string='Unit')
    name = fields.Many2one('bakers_archive.ingredient', string='Ingredient')
    notes = fields.Text(string='Notes')

    recipe_id = fields.Many2one('bakers_archive.recipe', String="Recipe ID", ondelete='cascade')
