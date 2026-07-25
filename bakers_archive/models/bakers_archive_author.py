from odoo import fields, models


class BakersArchiveAuthor(models.Model):
    _name = 'bakers_archive.author'
    _description = 'Bakers Archive Author'

    name = fields.Char(string='Name', required=True)
    biography = fields.Text(string='Biography')
    website = fields.Char(string='Website')
    recipe_ids = fields.Many2many('bakers_archive.recipe', string='Recipes')
    image_128 = fields.Image(string='Image')
