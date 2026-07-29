# -*- coding: utf-8 -*-
# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BakersArchiveRecipeInstruction(models.Model):
    _name = 'bakers_archive.recipe.instruction'
    _description = 'Bakers Archive Recipe Instruction'
    _order = 'sequence, id'

    name = fields.Char(string='Instruction Step', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    time = fields.Float(string='Time')

    recipe_id = fields.Many2one('bakers_archive.recipe', string='Recipe', ondelete='cascade', required=True)
    category_id = fields.Many2one('bakers_archive.recipe.instruction.category', string='Category', domain="[('recipe_id', '=', recipe_id)]")

