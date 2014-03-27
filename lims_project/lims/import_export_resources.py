from __future__ import print_function
import sys

import json
from import_export import resources, fields
from import_export.widgets import Widget

from lims.models import Sample, Container


class LIMSForeignKeyWidget(Widget):
    """
    Widget for ``ForeignKey`` model field that represent ForeignKey as
    integer value.

    Requires a positional argument: the class to which the field is related.
    """

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(LIMSForeignKeyWidget, self).__init__(*args, **kwargs)

    def clean(self, value):
        pk = super(LIMSForeignKeyWidget, self).clean(value)
        return self.model.objects.get(pk=pk) if pk else None

    def render(self, value):
        if value is None:
            return ""
        return str(value) + " (HAHAHA id=%d)" % value.pk


class ContainerResource(resources.ModelResource):
    class Meta:
        model = Container


class SampleResource(resources.ModelResource):
    #collaborator = fields.Field(attribute='collaborator', column_name='collaborator', widget=LIMSForeignKeyWidget(Collaborator))

    def before_import(self, dataset, dry_run):
        nr_core_sample_cols = 17
        extra_column_data = []

        for row in dataset:
            ecd_row = {}
            for i in range(nr_core_sample_cols, len(dataset.headers)):
                ecd_row[dataset.headers[i]] = row[i]
            extra_column_data.append(json.dumps(ecd_row))

        #print(dataset['extra_column1'], file=sys.stderr)
        del dataset['extra_columns_json']
        dataset.append_col(extra_column_data, header='extra_columns_json')
        #print(dataset['extra_columns_json'], file=sys.stderr)

    class Meta:
        model = Sample
