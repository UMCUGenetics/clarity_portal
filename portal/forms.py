from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, AnyOf
import re

from . import lims, app, utils


class SubmitSampleForm(FlaskForm):
    username = StringField('Gebruikersnaam', validators=[DataRequired()])
    indicationcode = StringField(
        'Indicatie code',
        validators=[DataRequired(), AnyOf(app.config['LIMS_INDICATIONS'].keys(), message='Foute indicatie code.')]
    )
    pool_fragment_length = DecimalField('Pool - Fragment lengte (bp)')
    pool_concentration = DecimalField('Pool - Concentratie (ng/ul)')
    samples = TextAreaField(
        'Samples',
        description=(
            "Een regel per sample en kolommen gescheiden door tabs."
            "Kolom volgorde: Sample naam, Barcode, Override Cycles, Exoom equivalenten, Sample type."
        ),
        validators=[DataRequired()]
    )
    attachment = FileField()

    # Filled in validation function.
    researcher = None
    parsed_samples = []
    sum_exome_count = 0

    def validate(self, extra_validators=[]):
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

            if len(data) < 4:
                self.samples.errors.append('Regel {0} bevat geen 4 kolommen: {1}.'.format(idx+1, data))
                return False  # Stop parsing sample data, because we can't continue without 4 columns.
            elif len(data) == 5:
                sample_type = data[4]

            try:
                sample = {
                    'name': data[0],
                    'barcode': data[1],
                    'override_cycles': data[2],
                    'exome_count': float(data[3]),
                    'type': sample_type
                }
            except ValueError:  # only possible for exome_count
                self.samples.errors.append('Regel {0}, kolom 4 is geen getal: {1}.'.format(idx+1, data[2]))
                return False

            # Check sample name prefix
            sample_name_prefixes = app.config['LIMS_INDICATIONS'][self.indicationcode.data]['sample_name_prefixes']
            sample_name_prefix_error = True
            for sample_name_prefix in sample_name_prefixes:
                if sample['name'].startswith(sample_name_prefix) and sample['name'] != sample_name_prefix:
                    sample_name_prefix_error = False

            # Check sample name
            sample_name_error = utils.substrings_in_list(app.config['SAMPLE_NAME_FORBIDDEN'], sample['name'])
            if sample_name_prefix_error or sample_name_error:
                self.samples.errors.append('Regel {0}, incorrecte sample naam: {1}.'.format(idx+1, sample['name']))
                sample_error = True
            if sample['name'] in sample_names:
                self.samples.errors.append('Regel {0}, dubbele sample naam: {1}.'.format(idx+1, sample['name']))
                sample_error = True
            else:
                sample_names.append(sample['name'])

            # Check reagents
            reagent_types = lims.get_reagent_types(name=sample['barcode'])
            if not reagent_types:
                self.samples.errors.append('Regel {0}, onbekende barcode: {1}.'.format(idx+1, sample['barcode']))
                sample_error = True
            elif len(reagent_types) > 1:
                self.samples.errors.append('Regel {0}, meerdere barcode matches in clarity lims: {1}.'.format(
                    idx+1, sample['barcode'])
                )
                sample_error = True
            elif sample['barcode'] in barcodes:
                self.samples.errors.append('Regel {0}, dubbele barcode: {1}.'.format(idx+1, sample['barcode']))
                sample_error = True
            else:
                sample['reagent_type'] = reagent_types[0]
                barcodes.append(sample['barcode'])

            # Check override_cycles
            if ';' not in sample['override_cycles']:
                self.samples.errors.append('Regel {0}, override_cycles moet gescheiden zijn door ;.'.format(idx+1))
                sample_error = True
            else:
                override_cycles = sample['override_cycles'].split(';')
                if len(override_cycles) != 4:
                    self.samples.errors.append('Regel {0}, override_cycles moet 4 cycli bevatten.'.format(idx+1))
                    sample_error = True
                else:
                    for cycle_idx, cycle in enumerate(override_cycles):
                        cycle_len = sum(map(int, re.findall(r'\d+', cycle)))
                        if cycle_len != app.config['OVERRIDE_CYCLES_LEN'][cycle_idx]:
                            self.samples.errors.append(
                                'Regel {0}, override_cycle {1} heeft een incorrecte lengte {2} in plaats van {3}.'.format(
                                    idx+1, cycle, cycle_len, app.config['OVERRIDE_CYCLES_LEN'][cycle_idx]
                                )
                            )
                            sample_error = True

            self.sum_exome_count += sample['exome_count']
            self.parsed_samples.append(sample)

        if sample_error:
            return False

        return True


class SubmitDXSampleForm(FlaskForm):
    username = StringField('Gebruikersnaam', validators=[DataRequired()])
    pool_fragment_length = DecimalField('Pool - Fragment lengte (bp)', validators=[DataRequired()])
    pool_concentration = DecimalField('Pool - Concentratie (ng/ul)', validators=[DataRequired()])
    samples = TextAreaField(
        'Samples',
        description=(
            "Een regel per sample en kolommen gescheiden door tabs."
            "Kolom volgorde: Sample naam, Barcode, Exoom equivalenten, Sample type, Project naam."
        ),
        validators=[DataRequired()]
    )
    helix_worklist = FileField('Helix Werklijst', validators=[DataRequired()])

    # Filled in validation function.
    researcher = None
    parsed_samples = []
    sum_exome_count = 0

    def validate(self, extra_validators=[]):
        """Extra validation, used to validate submitted samples."""
        self.parsed_samples = {}
        self.parsed_worklist = {}
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
            sample_project = ''

            if len(data) != 5:
                self.samples.errors.append('Regel {0} bevat geen 3 kolommen: {1}.'.format(idx+1, data))
                sample_error = True
            sample_type = data[3]
            sample_project = data[4]

            try:
                sample = {
                    'name': data[0],
                    'barcode': data[1],
                    'exome_count': float(data[2]),
                    'type': sample_type,
                    'project': sample_project
                }
            except ValueError:  # only possible for exome_count
                self.samples.errors.append('Regel {0}, kolom 3 is geen getal: {1}.'.format(idx+1, data[2]))
                sample_error = True

            # Check sample name
            sample_name_error = utils.substrings_in_list(app.config['SAMPLE_NAME_FORBIDDEN'], sample['name'])
            if sample_name_error:
                self.samples.errors.append('Regel {0}, incorrecte sample naam: {1}.'.format(idx+1, sample['name']))
                sample_error = True
            if sample['name'] in sample_names:
                self.samples.errors.append('Regel {0}, dubbele sample naam: {1}.'.format(idx+1, sample['name']))
                sample_error = True
            else:
                sample_names.append(sample['name'])

            # Check reagents
            reagent_types = lims.get_reagent_types(name=sample['barcode'])
            if not reagent_types:
                self.samples.errors.append('Regel {0}, onbekende barcode: {1}.'.format(idx+1, sample['barcode']))
                sample_error = True
            elif len(reagent_types) > 1:
                self.samples.errors.append('Regel {0}, meerdere barcode matches in clarity lims: {1}.'.format(
                    idx+1, sample['barcode'])
                )
                sample_error = True
            elif sample['barcode'] in barcodes:
                self.samples.errors.append('Regel {0}, dubbele barcode: {1}.'.format(idx+1, sample['barcode']))
                sample_error = True
            else:
                sample['reagent_type'] = reagent_types[0]
                barcodes.append(sample['barcode'])

            # Check Sample typo
            valid_sample_types = ['RNA library', 'DNA library']
            if sample['type'] not in valid_sample_types:
                self.samples.errors.append('Regel {0}, onbekende sample type: {1} (Kies uit: {2}).'.format(
                    idx+1, sample['type'], ', '.join(valid_sample_types))
                )
                sample_error = True

            self.sum_exome_count += sample['exome_count']
            self.parsed_samples[sample['name']] = sample

        # Parse helix_worklist
        header = []
        udf_column = {
            'Dx Onderzoeknummer': {'column': 'Onderzoeknummer'},
            'Dx Fractienummer': {'column': 'Fractienummer'},
            'Dx Monsternummer': {'column': 'Monsternummer'},
            'Dx Concentratie (ng/ul)': {'column': 'Concentratie (ng/ul)'},
            'Dx Materiaal type': {'column': 'Materiaal'},
            'Dx Foetus': {'column': 'Foetus'},
            'Dx Foetus geslacht': {'column': 'Foetus_geslacht'},
            'Dx Overleden': {'column': 'Overleden'},
            'Dx Opslaglocatie': {'column': 'Opslagpositie'},
            'Dx Spoed': {'column': 'Spoed'},
            'Dx NICU Spoed': {'column': 'NICU Spoed'},
            'Dx Persoons ID': {'column': 'Persoons_id'},
            'Dx Werklijstnummer': {'column': 'Werklijstnummer'},
            'Dx Familienummer': {'column': 'Familienummer'},
            'Dx Geslacht': {'column': 'Geslacht'},
            'Dx Geboortejaar': {'column': 'Geboortejaar'},
            'Dx Meet ID': {'column': 'Stof_meet_id'},
            'Dx Stoftest code': {'column': 'Stoftestcode'},
            'Dx Stoftest omschrijving': {'column': 'Stoftestomschrijving'},
            'Dx Onderzoeksindicatie': {'column': 'Onderzoeksindicatie'},
            'Dx Onderzoeksreden': {'column': 'Onderzoeksreden'},
            'Dx Protocolcode': {'column': 'Protocolcode'},
            'Dx Protocolomschrijving': {'column': 'Protocolomschrijving'},
        }

        for line in self.helix_worklist.data:
            line = line.decode('utf-8')
            if not header:
                header = line.rstrip().split(',')
                for udf in udf_column:
                    udf_column[udf]['index'] = header.index(udf_column[udf]['column'])
            else:
                data = re.sub(r'"+(\w+)"+', r'"\g<1>"', line).strip()[1:-1].split('","')
                sample_name = data[header.index('Monsternummer')]
                udf_data = {'Dx Import warning': ''}
                for udf in udf_column:
                    # Transform specific udf
                    try:
                        if udf in ['Dx Overleden', 'Dx Spoed', 'Dx NICU Spoed']:
                            udf_data[udf] = utils.char_to_bool(data[udf_column[udf]['index']])
                        elif udf in ['Dx Geslacht', 'Dx Foetus geslacht']:
                            udf_data[udf] = utils.transform_sex(data[udf_column[udf]['index']])
                        elif udf == 'Dx Foetus':
                            udf_data[udf] = bool(data[udf_column[udf]['index']].strip())
                        elif udf == 'Dx Concentratie (ng/ul)':
                            udf_data[udf] = data[udf_column[udf]['index']].replace(',', '.')
                        else:
                            udf_data[udf] = data[udf_column[udf]['index']]
                    except ValueError as e:
                        self.helix_worklist.errors.append("Kolom '{0}' fout: {1}".format(udf_column[udf]['column'], e))
                        return False

                # Set 'Dx Handmatig' udf
                if (
                    udf_data['Dx Foetus'] or
                    udf_data['Dx Overleden'] or
                    udf_data['Dx Materiaal type'] not in ['BL', 'BLHEP', 'BM', 'BMEDTA']
                ):
                    udf_data['Dx Handmatig'] = True
                else:
                    udf_data['Dx Handmatig'] = False

                # Set 'Dx Familie status' udf
                if udf_data['Dx Onderzoeksreden'] == 'Bevestiging diagnose':
                    udf_data['Dx Familie status'] = 'Kind'
                elif udf_data['Dx Onderzoeksreden'] == 'Prenataal onderzoek':
                    udf_data['Dx Familie status'] = 'Kind'
                elif udf_data['Dx Onderzoeksreden'] == 'Informativiteitstest':
                    udf_data['Dx Familie status'] = 'Ouder'
                else:
                    udf_data['Dx Import warning'] = ';'.join(
                        ['Onbekende onderzoeksreden, familie status niet ingevuld.', udf_data['Dx Import warning']]
                    )

                # Set 'Dx Geslacht' and 'Dx Geboortejaar' with 'Foetus' information if 'Dx Foetus == True'
                if udf_data['Dx Foetus']:
                    udf_data['Dx Geslacht'] = udf_data['Dx Foetus geslacht']
                    udf_data['Dx Geboortejaar'] = ''

                # Set 'Dx Geslacht = Onbekend' if 'Dx Onderzoeksindicatie == DSD00'
                if udf_data['Dx Onderzoeksindicatie'] == 'DSD00' and udf_data['Dx Familie status'] == 'Kind':
                    udf_data['Dx Geslacht'] = 'Onbekend'

                # Check 'Dx Familienummer' and correct
                if '/' in udf_data['Dx Familienummer']:
                    udf_data['Dx Import warning'] = ';'.join([
                        'Meerdere familienummers, laatste wordt gebruikt. ({0})'.format(udf_data['Dx Familienummer']),
                        udf_data['Dx Import warning']
                    ])
                    udf_data['Dx Familienummer'] = udf_data['Dx Familienummer'].split('/')[-1].strip(' ')
                self.parsed_worklist[sample_name] = udf_data

        # Check parsed_samples and parsed_worklist
        parsed_samples_keys = sorted(self.parsed_samples.keys())
        parsed_worklist_keys = sorted(self.parsed_worklist.keys())
        if parsed_samples_keys != parsed_worklist_keys:
            self.samples.errors.append('Samples komen niet overeen met samples in helix werklijst.')
            sample_error = True

        if sample_error:
            return False

        return True
