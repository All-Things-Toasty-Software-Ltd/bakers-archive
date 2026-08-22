# Part of The Baker's Archive. See LICENSE file for full copyright and licensing details.

import base64
from datetime import date, datetime
from decimal import Decimal


class BakersArchiveModelSerializer:
    """
    Generic serializer for Bakers Archive Odoo models.

    The serializer automatically expands relationships between models whose
    technical name begins with ``bakers_archive.``.

    Relationships to external Odoo models are represented as shallow
    references rather than recursively serialised. This prevents the API from
    accidentally walking through the entire Odoo relational graph.
    """

    MODEL_PREFIX = 'bakers_archive.'

    DEFAULT_MAX_DEPTH = 10

    def __init__(self, max_depth=None):
        """
        :param max_depth:
            Maximum number of recursive relationships to follow.
            ``None`` uses ``DEFAULT_MAX_DEPTH``.
        """
        if max_depth is None:
            max_depth = self.DEFAULT_MAX_DEPTH

        self.max_depth = max(0, int(max_depth))

    def serialize(self, record):
        """
        Serialise an Odoo record or singleton recordset.

        Empty recordsets return ``None``.
        """
        if not record or not record.exists():
            return None

        record.ensure_one()

        return self._serialize_record(
            record,
            depth=0,
            visited=set(),
        )

    def _serialize_record(self, record, depth, visited):
        """
        Serialise a single Odoo record.
        """
        record.ensure_one()

        record_key = (record._name, record.id)

        # Once a record has already appeared in the current path, return a
        # shallow reference instead of descending into it again.
        if record_key in visited:
            return self._serialize_reference(record)

        # Respect the maximum depth.
        if depth > self.max_depth:
            return self._serialize_reference(record)

        visited = visited | {record_key}

        fields = []

        for field_name, field in record._fields.items():
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
            'display_name': self._make_json_safe(
                record.display_name
            ),
            'reference': False,
            'fields': fields,
        }

    def _serialize_field(
            self,
            record,
            field_name,
            field,
            depth,
            visited,
    ):
        """
        Serialise one Odoo field.
        """

        try:
            value = record[field_name]
        except Exception as error:
            return {
                'name': field_name,
                'label': field.string or field_name,
                'type': field.type,
                'value': None,
                'error': (
                        'Unable to read field: %s'
                        % self._make_json_safe(error)
                ),
            }

        data = {
            'name': field_name,
            'label': field.string or field_name,
            'type': field.type,
        }

        try:
            if field.type == 'many2one':
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

            elif field.type == 'reference':
                data['value'] = self._serialize_relation(
                    value,
                    depth=depth,
                    visited=visited,
                )

            elif field.type == 'selection':
                data['value'] = self._make_json_safe(value)
                data['selection'] = self._serialize_selection(
                    field,
                    record,
                )

            elif field.type == 'binary':
                data['value'] = self._serialize_binary(value)

            else:
                data['value'] = self._make_json_safe(value)

        except Exception as error:
            # The field itself is still useful metadata even if its value cannot be serialised.
            data['value'] = None
            data['error'] = (
                    'Unable to serialise field: %s'
                    % self._make_json_safe(error)
            )

        return data

    def _serialize_relation(self, record, depth, visited):
        """
        Serialise a relational value.

        Bakers Archive models are recursively expanded.

        External Odoo models are represented by a shallow reference.
        """
        if not record:
            return None

        if not hasattr(record, '_name'):
            return self._make_json_safe(record)

        # Only Bakers Archive models are recursively expanded.
        if not self._should_expand_model(record._name):
            return self._serialize_reference(record)

        return self._serialize_record(
            record,
            depth=depth + 1,
            visited=visited,
        )

    def _should_expand_model(self, model_name):
        """
        Return whether the model belongs to Bakers Archive and may therefore
        be recursively expanded.
        """
        return model_name.startswith(self.MODEL_PREFIX)

    def _serialize_reference(self, record):
        """
        Return a shallow reference to an Odoo record.

        This is used for:

        - external Odoo models
        - circular references
        - records beyond the configured maximum depth
        """
        if not record:
            return None

        # A relational value should normally be a singleton here.
        if len(record) != 1:
            return [
                self._serialize_reference(single_record)
                for single_record in record
            ]

        record.ensure_one()

        return {
            'model': record._name,
            'model_label': record._description,
            'id': record.id,
            'display_name': self._make_json_safe(
                record.display_name
            ),
            'reference': True,
        }

    def _serialize_selection(self, field, record):
        """
        Return a JSON-safe representation of a selection field.
        """
        selection = None

        try:
            selection = field._description_selection(
                record.env
            )
        except Exception:
            selection = field.selection

            if callable(selection):
                try:
                    selection = selection(record)
                except TypeError:
                    selection = selection()

            elif isinstance(selection, str):
                method = getattr(record, selection, None)

                if callable(method):
                    selection = method()

        if not selection:
            return []

        result = []

        for item in selection:
            if (
                    isinstance(item, (list, tuple))
                    and len(item) >= 2
            ):
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

    def _serialize_binary(self, value):
        """
        Make binary data JSON-safe.
        """
        if not value:
            return None

        if isinstance(value, str):
            return value

        if isinstance(value, bytes):
            return base64.b64encode(value).decode('ascii')

        return self._make_json_safe(value)

    def _make_json_safe(self, value):
        """
        Convert Python and Odoo values into JSON-compatible values.
        """

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
            return {
                str(key): self._make_json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple, set)):
            return [
                self._make_json_safe(item)
                for item in value
            ]

        if hasattr(value, '_name') and hasattr(value, 'ids'):
            if len(value) == 1:
                return self._serialize_reference(value)

            return [
                self._serialize_reference(record)
                for record in value
            ]

        if hasattr(value, 'isoformat'):
            try:
                return value.isoformat()
            except Exception:
                pass

        return str(value)
