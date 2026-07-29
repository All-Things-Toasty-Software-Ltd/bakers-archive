# -*- coding: utf-8 -*-
# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class BakersArchiveRecipeInstructionCategory(models.Model):
    _name = 'bakers_archive.recipe.instruction.category'
    _description = 'Bakers Archive Recipe Instruction Category'
    _order = 'sequence, id'

    name = fields.Text(string='Category Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    recipe_id = fields.Many2one('bakers_archive.recipe', string='Recipe', ondelete='cascade', required=True)