from odoo import fields, models


class BakersArchiveTagCategory(models.Model):
    _name = 'bakers_archive.tag.category'
    _description = 'Bakers Archive Tag Category'
    _order = 'name'

    name = fields.Char('Name', required=True, translate=True)
    tag_ids = fields.One2many('bakers_archive.tag', 'category_id', string='Tags')

    _name_uniq = models.Constraint(
        'unique (name)',
        'Tag name already exists!',
    )
