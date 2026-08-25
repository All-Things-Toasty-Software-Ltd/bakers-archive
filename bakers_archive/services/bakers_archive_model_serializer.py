# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

import base64
from datetime import date, datetime
from decimal import Decimal


class BakersArchiveModelSerializer:
    """
    Generic serializer for Bakers Archive Odoo models.
    """

    MODEL_PREFIX = 'bakers_archive.'
    DEFAULT_MAX_DEPTH = 3

    # Fields that should never be serialized over the API
    EXCLUDED_FIELDS = {
        'create_uid',
        'write_uid',
        'create_date',
        'write_date',
        '__last_update',
        'display_name',
    }

    def __init__(self, max_depth=None):
        if max_depth is None:
            max_depth = self.DEFAULT_MAX_DEPTH
        self.max_depth = max(0, int(max_depth))

    def serialize(self, record):
        if not record or not record.exists():
            return None

        record.ensure_one()

        # Shared visited set across the entire serialization traversal tree
        visited = set()

        return self._serialize_record(
            record,
            depth=0,
            visited=visited,
        )

    def _serialize_record(self, record, depth, visited):
        record.ensure_one()
        record_key = (record._name, record.id)

        if record_key in visited or depth > self.max_depth:
            return self._serialize_reference(record)

        # Mutate shared set directly
        visited.add(record_key)

        fields = []

        for field_name, field in record._fields.items():
            # Skip system/technical fields and raw binary blobs by default
            if field_name in self.EXCLUDED_FIELDS or field.type == 'binary':
                continue

            field_data = self._serialize_field(
                record=record,
                field_name=field_name,
                field=field,
                depth=depth,
                visited=visited,
            )

            if field_data is not None:
                fields.append(field_data)

        return {
            'model': record._name,
            'model_label': record._description,
            'id': record.id,
            'display_name': self._make_json_safe(record.display_name),
            'reference': False,
            'fields': fields,
        }

    def _serialize_field(self, record, field_name, field, depth, visited):
        try:
            value = record[field_name]
        except Exception as error:
            return {
                'name': field_name,
                'label': field.string or field_name,
                'type': field.type,
                'value': None,
                'error': f'Unable to read field: {self._make_json_safe(error)}',
            }

        data = {
            'name': field_name,
            'label': field.string or field_name,
            'type': field.type,
        }

        try:
            if field.type in ('many2one', 'reference'):
                data['value'] = self._serialize_relation(
                    value,
                    depth=depth,
                    visited=visited,
                )

            elif field.type in ('one2many', 'many2many'):
                data['value'] = [
                    self._serialize_relation(
                        related_record,
                        depth=depth,
                        visited=visited,
                    )
                    for related_record in value
                ]

            elif field.type == 'selection':
                data['value'] = self._make_json_safe(value)
                data['selection'] = self._serialize_selection(field, record)

            else:
                data['value'] = self._make_json_safe(value)

        except Exception as error:
            data['value'] = None
            data['error'] = f'Unable to serialise field: {self._make_json_safe(error)}'

        return data

    def _serialize_relation(self, record, depth, visited):
        if not record:
            return None

        if not hasattr(record, '_name'):
            return self._make_json_safe(record)

        if not self._should_expand_model(record._name):
            return self._serialize_reference(record)

        return self._serialize_record(
            record,
            depth=depth + 1,
            visited=visited,
        )

    def _should_expand_model(self, model_name):
        return model_name.startswith(self.MODEL_PREFIX)

    def _serialize_reference(self, record):
        if not record:
            return None

        if len(record) != 1:
            return [self._serialize_reference(r) for r in record]

        record.ensure_one()

        return {
            'model': record._name,
            'model_label': record._description,
            'id': record.id,
            'display_name': self._make_json_safe(record.display_name),
            'reference': True,
        }

    def _serialize_selection(self, field, record):
        selection = None
        try:
            selection = field._description_selection(record.env)
        except Exception:
            selection = field.selection
            if callable(selection):
                try:
                    selection = selection(record)
                except TypeError:
                    selection = selection()

        if not selection:
            return []

        result = []
        for item in selection:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                result.append({
                    'value': self._make_json_safe(item[0]),
                    'label': self._make_json_safe(item[1]),
                })
            else:
                result.append({
                    'value': self._make_json_safe(item),
                    'label': self._make_json_safe(item),
                })
        return result

    def _make_json_safe(self, value):
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        if isinstance(value, bytes):
            return base64.b64encode(value).decode('ascii')
        if isinstance(value, dict):
            return {str(k): self._make_json_safe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._make_json_safe(item) for item in value]
        if hasattr(value, '_name') and hasattr(value, 'ids'):
            if len(value) == 1:
                return self._serialize_reference(value)
            return [self._serialize_reference(r) for r in value]

        return str(value)
