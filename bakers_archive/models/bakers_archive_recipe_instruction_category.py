from odoo import fields, models


class BakersArchiveRecipeInstructionCategory(models.Model):
    _name = 'bakers_archive.recipe.instruction.category'
    _description = 'Bakers Archive Recipe Instruction Category'
    _order = 'sequence'

    instruction_ids = fields.One2many('bakers_archive.recipe.instruction', 'category_id', string='Tags')

    sequence = fields.Integer(string='Sequence')
    name = fields.Text(string='Category')
