from odoo import fields, models


class BakersArchiveCoreLanguage(models.Model):
    _name = 'bakers_archive.core.language'
    _description = 'Bakers Archive Core Language'

    language = fields.Char(string='Language', required=True)
    recipe_ids = fields.Many2many('bakers_archive.core.recipe', string='Recipes')
