import os
from time import gmtime, strftime

from flask import render_template, url_for, redirect

from . import app
from .forms import SequencingRunForm


@app.route('/')
def index():
    return redirect(url_for('removed_samples'))


@app.route('/removed_samples')
def removed_samples():
    removed_samples_file = app.config['REMOVED_SAMPLES_FILE']

    if os.path.exists(removed_samples_file):
        t = os.path.getmtime(removed_samples_file)
        date = strftime("%d %b %Y", gmtime(t))
        time = strftime("%H:%M:%S", gmtime(t))

        with open(removed_samples_file, 'r') as f:
            # Parse header
            line_data = f.readline().rstrip().split('\t')
            header = {
                    'head1': line_data[0],
                    'head2': line_data[1],
                    'head3': line_data[2],
                    'head4': line_data[3],
                    'head5': line_data[4],
                    'head6': line_data[5]
                }

            # Parse samples
            samples = []
            for line in f:
                line_data = line.rstrip().split('\t')
                samples.append(
                    {
                        'col1': line_data[0],
                        'col2': line_data[1],
                        'col3': line_data[2],
                        'col4': line_data[3],
                        'col5': line_data[4],
                        'col6': line_data[5]
                    }
                )
        return render_template('removed_samples.html', title='Verwijderde samples', header=header, samples=samples, date=date, time=time)
    else:
        return render_template('no_file.html', title='Verwijderde samples')


@app.route('/submit_samples', methods=['GET', 'POST'])
def submit_samples():
    form = SequencingRunForm()

    if form.validate_on_submit():
        print form.data

    return render_template('submit_samples.html', title='Submit samples', form=form,)
