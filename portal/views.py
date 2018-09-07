import os
from time import gmtime, strftime
from datetime import date
from xml.dom import minidom

from flask import render_template, url_for, redirect
from genologics.entities import Sample, Project, Containertype, Container, Workflow

from . import app, lims
from .forms import SubmitSampleForm


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
                    'head6': line_data[5],
                    'head7': line_data[6],
                    'head8': line_data[7]
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
                        'col6': line_data[5],
                        'col7': line_data[6],
                        'col8': line_data[7]
                    }
                )
        return render_template('removed_samples.html', title='Verwijderde samples', header=header, samples=samples, date=date, time=time)
    else:
        return render_template('no_file.html', title='Verwijderde samples')


@app.route('/submit_samples', methods=['GET', 'POST'])
def submit_samples():
    form = SubmitSampleForm()

    if form.validate_on_submit():
        # Create lims project
        project_name = '{prefix}_{week}'.format(
            prefix=app.config['LIMS_INDICATIONS'][form.indicationcode.data]['project_name_prefix'],
            week=date.today().isocalendar()[1]
        )
        lims_project = Project.create(lims, name=project_name, researcher=form.researcher, udf={'Application': form.indicationcode.data})

        # Create Samples
        lims_container_type = Containertype(lims, id='2')  # Tube
        sample_artifacts = []
        for sample in form.parsed_samples:
            lims_container = Container.create(lims, type=lims_container_type, name=sample['name'])
            sample_udf_data = {
                'Sample Type': 'DNA library',
                'Dx Fragmentlengte (bp) Externe meting': form.pool_fragment_length.data,
                'Dx Conc. (ng/ul) Externe meting': form.pool_concentration.data,
                'Dx Exoomequivalent': form.sum_exoom_count,
                'Dx sequencing project': app.config['LIMS_INDICATIONS'][form.indicationcode.data]['sequencing_project'],
            }
            lims_sample = Sample.create(lims, container=lims_container, position='1:1', project=lims_project, name=sample['name'], udf=sample_udf_data)
            print lims_sample.name, lims_sample.artifact.name
            artifact = lims_sample.artifact
            sample_artifacts.append(artifact)

            # Add reagent label (barcode)
            artifact_xml_dom = minidom.parseString(artifact.xml())
            for artifact_name_node in artifact_xml_dom.getElementsByTagName('name'):
                parent = artifact_name_node.parentNode
                reagent_label = artifact_xml_dom.createElement('reagent-label')
                reagent_label.setAttribute('name', sample['barcode'])
                parent.appendChild(reagent_label)
                lims.put(artifact.uri, artifact_xml_dom.toxml(encoding='utf-8'))

        # Route artifacts to workflow
        workflow = Workflow(lims, id=app.config['LIMS_INDICATIONS'][form.indicationcode.data]['workflow_id'])
        lims.route_artifacts(sample_artifacts, workflow_uri=workflow.uri)

        return render_template('submit_samples_done.html', title='Submit samples', project_name=project_name, form=form)
    return render_template('submit_samples.html', title='Submit samples', form=form)
