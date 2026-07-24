from odoo import fields, models


class BakersArchiveCoreAuthor(models.Model):
    _name = 'bakers_archive.core.author'
    _description = 'Bakers Archive Core Author'

    name = fields.Char(string='Name', required=True)
    biography = fields.Text(string='Biography')
    website = fields.Website(string='Website')
    recipe_ids = fields.Many2many('bakers_archive.core.recipe', string='Recipes')
