from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, AnyOf

from . import lims, app


class SubmitSampleForm(FlaskForm):
    username = StringField('Gebruikersnaam', validators=[DataRequired()])
    indicationcode = StringField('Indicatie code', validators=[DataRequired(), AnyOf(app.config['LIMS_INDICATIONS'].keys(), message='Foute indicatie code')])
    pool_fragment_length = DecimalField('Pool - Fragment lengte (bp)')
    pool_concentration = DecimalField('Pool - Concentratie (ng/ul)')
    samples = TextAreaField(
        'Samples',
        description="Een regel per sample en kolommen gescheiden door tabs. Kolom volgorde: Sample naam, Barcode, Exoom equivalenten, Sample type.",
        validators=[DataRequired()]
    )
    attachment = FileField()

    # Filled in validation function.
    researcher = None
    parsed_samples = []
    sum_exome_count = 0

    def validate(self):
        """Extra validation, used to validate submitted samples."""
        self.parsed_samples = []
        self.sum_exome_count = 0
        sample_names = []
        barcodes = []

        if not FlaskForm.validate(self):
            return False

        # Check researcher
        try:
            self.researcher = lims.get_researchers(username=self.username.data)[0]
        except IndexError:
            self.username.errors.append('Gebruikersnaam bestaat niet.')
            return False

        # Parse samples data
        sample_error = False
        for idx, line in enumerate(self.samples.data.split('\n')):
            data = line.strip().split('\t')
            sample_type = ''

            if len(data) < 3:
                self.samples.errors.append('Regel {0} bevat geen 3 kolommen: {1}'.format(idx+1, data))
                sample_error = True
            elif len(data) == 4:
                sample_type = data[3]

            try:
                sample = {'name': data[0], 'barcode': data[1], 'exome_count': float(data[2]), 'type': sample_type}
            except ValueError:  # only possible for exome_count
                self.samples.errors.append('Regel {0}, kolom 3 is geen getal: {1}'.format(idx+1, data[2]))
                sample_error = True

            # Check sample name prefix
            sample_name_prefixes = app.config['LIMS_INDICATIONS'][self.indicationcode.data]['sample_name_prefixes']
            sample_name_prefix_error = True
            for sample_name_prefix in sample_name_prefixes:
                if sample['name'].startswith(sample_name_prefix) and sample['name'] != sample_name_prefix:
                    sample_name_prefix_error = False

            # Check sample name
            if sample_name_prefix_error or '_' in sample['name']:
                self.samples.errors.append('Regel {0}, incorrecte sample naam: {1}'.format(idx+1, sample['name']))
                sample_error = True
            if sample['name'] in sample_names:
                self.samples.errors.append('Regel {0}, dubbele sample naam: {1}'.format(idx+1, sample['name']))
                sample_error = True
            else:
                sample_names.append(sample['name'])

            # Check reagents
            reagent_types = lims.get_reagent_types(name=sample['barcode'])
            if not reagent_types:
                self.samples.errors.append('Regel {0}, onbekende barcode: {1}'.format(idx+1, sample['barcode']))
                sample_error = True
            elif len(reagent_types) > 1:
                self.samples.errors.append('Regel {0}, meerdere barcode matches in clarity lims: {1}'.format(idx+1, sample['barcode']))
                sample_error = True
            elif sample['barcode'] in barcodes:
                self.samples.errors.append('Regel {0}, dubbele barcode: {1}'.format(idx+1, sample['barcode']))
                sample_error = True
            else:
                sample['reagent_type'] = reagent_types[0]
                barcodes.append(sample['barcode'])

            self.sum_exome_count += sample['exome_count']
            self.parsed_samples.append(sample)

        if self.sum_exome_count > 51:
            self.samples.errors.append('Totaal aantal exoom equivalenten ({0}) is groter dan 51.'.format(self.sum_exome_count))
            sample_error = True

        if sample_error:
            return False

        return True
