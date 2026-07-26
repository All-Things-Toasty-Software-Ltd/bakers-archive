from odoo import fields, models


class BakersArchiveOrigin(models.Model):
    _name = 'bakers_archive.origin'
    _description = 'Bakers Archive Origin'

    name = fields.Char(string='Country', required=True)
    recipe_ids = fields.Many2many('bakers_archive.recipe', string='Recipes')