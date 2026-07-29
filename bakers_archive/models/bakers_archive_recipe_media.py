from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BakersArchiveRecipeMedia(models.Model):
    _name = 'bakers_archive.recipe.media'
    _description = 'Bakers Archive Recipe Media'
    _order = 'sequence, id'

    name = fields.Char(string='Title', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')

    recipe_id = fields.Many2one('bakers_archive.recipe', string='Recipe', ondelete='cascade', required=True)

    media_type = fields.Selection([
        ('image', 'Image'),
        ('video_link', 'Video Link'),
        ('other_link', 'Other Link'),
        ('document', 'Document'),
    ], string='Media Types', default='image', required=True)

    image = fields.Image(string='Image', max_width=1920, max_height=1920)
    video_url = fields.Char(string='Video URL', help='e.g., YouTube')
    other_link_url = fields.Char(string='Link URL', help='Any other relevant web link')

    attachment_id = fields.Many2one('ir.attachment', string='Attached File')

    display_media = fields.Html(string='Media Preview', compute='_compute_display_media')

    @api.depends('media_type', 'image', 'video_url', 'other_link_url')
    def _compute_display_media(self):
        for record in self:
            if record.media_type == 'image' and record.image:
                record.display_media = f'<img src="/web/image/{record._name}/{record.id}/image" style="max-width:150px; max-height:150px;"/>'
            elif record.media_type == 'video_link' and record.video_url:
                record.display_media = f'<a href="{record.video_url}" target="_blanl">{record.video_url}</a>'
            elif record.media_type == 'other_link' and record.other_link_url:
                record.display_media = f'<a href="{record.other_link_url}" target="_blank">{record.other_link_url}</a>'
            else:
                record.display_media = False

    @api.constrains('media_type', 'video_url', 'other_link_url')
    def _check_media_content(self):
        for record in self:
            if record.media_type == 'video_link' and not record.video_url:
                raise ValidationError("Video Link type requires a Video URL.")
            elif record.media_type == 'other_link' and not record.other_link_url:
                raise ValidationError("Other Link type requires a Link URL.")