"""Clarity Portal configuration."""

# Website
SECRET_KEY = 'change_this'
REMOVED_SAMPLES_FILE = 'path/to/removed_samples.txt'
LIMS_INDICATIONS = {
    'PD-PMC001': {
        'project_name_prefix': 'PMC_DXweek',
        'sample_name_prefixes': ['PM'],
        'workflow_id': '701',  # Dx Sequence facility v1.1
    },
    'RNA_seq': {
        'project_name_prefix': 'DX_RNASeq_week',
        'sample_name_prefixes': ['U'],
        'workflow_id': '701',  # Dx Sequence facility v1.1
    }
}


# Genologics
BASEURI = 'change_this'
USERNAME = 'change_this'
PASSWORD = 'change_this'
