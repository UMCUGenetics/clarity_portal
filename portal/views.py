from flask import render_template
from portal import app
import os
import datetime
from time import gmtime, strftime

@app.route('/')
@app.route('/index')
def index():
    samples = []
    header = []
    try:
        t = os.path.getmtime('data_files/removed_samples.txt')
        date = strftime("%d %b %Y", gmtime(t))
        time = strftime("%H:%M:%S", gmtime(t))
        with open('data_files/removed_samples.txt', 'r') as f:
            teller = 0
            for line in f:
                line_data = line.rstrip().split('\t')
                if teller == 0:
                    header.append(
                        {
                            'head1': line_data[0],
                            'head2': line_data[1],
                            'head3': line_data[2],
                            'head4': line_data[3],
                            'head5': line_data[4],
                            'head6': line_data[5]
                        }
                    )
                else:
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
                teller = teller + 1
        return render_template('removed_samples.html', title='Verwijderde samples Clarity LIMS', header=header, samples=samples, date=date, time=time)
    except:
        return render_template('no_file.html', title='Verwijderde samples Clarity LIMS')

@app.route('/removed_samples')
def removed_samples():
    samples = []
    header = []
    try:
        t = os.path.getmtime('data_files/removed_samples.txt')
        date = strftime("%d %b %Y", gmtime(t))
        time = strftime("%H:%M:%S", gmtime(t))
        with open('data_files/removed_samples.txt', 'r') as f:
            teller = 0
            for line in f:
                line_data = line.rstrip().split('\t')
                if teller == 0:
                    header.append(
                        {
                            'head1': line_data[0],
                            'head2': line_data[1],
                            'head3': line_data[2],
                            'head4': line_data[3],
                            'head5': line_data[4],
                            'head6': line_data[5]
                        }
                    )
                else:
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
                teller = teller + 1
        return render_template('removed_samples.html', title='Verwijderde samples Clarity LIMS', header=header, samples=samples, date=date, time=time)
    except:
        return render_template('no_file.html', title='Verwijderde samples Clarity LIMS')
