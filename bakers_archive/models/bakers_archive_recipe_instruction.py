from odoo import fields, models


class BakersArchiveRecipeInstruction(models.Model):
    _name = 'bakers_archive.recipe.instruction'
    _description = 'Bakers Archive Recipe Instruction'
    _order = 'sequence'

    recipe_id = fields.Many2one('bakers_archive.recipe', string='Recipe')

    sequence = fields.Integer(string='Sequence')
    name = fields.Text(string='Instruction')
    time = fields.Float(string='Time')
