from odoo import fields, models


class BakersArchiveCoreRecipeInstruction(models.Model):
    _name = 'bakers_archive.core.recipe.instruction'
    _description = 'Bakers Archive Core Recipe Instruction'
    _order = 'sequence'

    recipe_id = fields.Many2one('bakers_archive.core.recipe', string='Recipe')

    sequence = fields.Integer(string='Sequence')
    description = fields.Text(string='Description')
    time = fields.Float(string='Time')
