from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FormField, FieldList
from wtforms.validators import DataRequired, NumberRange


class SampleForm(FlaskForm):
    sample_name = StringField('Sample naam', validators=[DataRequired()])
    barcode = StringField('Sample barcode', validators=[DataRequired()])
    exome_equivalent = IntegerField('Exoom equivalenten', validators=[NumberRange(min=1)])


class SequencingRunForm(FlaskForm):
    indication_code = StringField('Indicatiecode', validators=[DataRequired()])
    samples = FieldList(FormField(SampleForm), min_entries=1)  # NOTE: do we need to set max_entries?
