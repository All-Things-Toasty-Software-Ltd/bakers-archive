from odoo import fields, models


class BakersArchiveCoreOrigin(models.Model):
    _name = 'bakers_archive.core.origin'
    _description = 'Bakers Archive Core Origin'

    country = fields.Char(string='Country', required=True)
    recipe_ids = fields.Many2many('bakers_archive.core.recipe', string='Recipes')
