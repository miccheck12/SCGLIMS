from __future__ import print_function
import sys

import json
from import_export import resources

from lims.models import Sample


class SampleResource(resources.ModelResource):
    def before_import(self, dataset, dry_run):
        nr_core_sample_cols = 17
        extra_column_data = []

        for row in dataset:
            ecd_row = {}
            for i in range(nr_core_sample_cols, len(dataset.headers)):
                ecd_row[dataset.headers[i]] = row[i]
            extra_column_data.append(json.dumps(ecd_row))

        print(dataset['extra_column1'], file=sys.stderr)
        del dataset['notes']
        dataset.append_col(extra_column_data, header='notes')
        print(dataset['notes'], file=sys.stderr)

    class Meta:
        model = Sample
