"""Clarity Portal configuration."""

# Website
SECRET_KEY = 'change_this'
REMOVED_SAMPLES_FILE = 'path/to/removed_samples.txt'
LIMS_INDICATIONS = {
    'PD-PMC001': {
        'project_name_prefix': 'PMC_DX',
        'sample_name_prefixes': ['PM'],
        'workflow_id': '701',  # Dx Sequence facility v1.1
        'email_to':[
            'change@email.nl',
        ]
    },
    'RNA_seq': {
        'project_name_prefix': 'DX_RNASeq',
        'sample_name_prefixes': ['U'],
        'workflow_id': '701',  # Dx Sequence facility v1.1
        'email_to':[
            'change@email.nl',
        ]
    }
}

# Genologics
BASEURI = 'change_this'
USERNAME = 'change_this'
PASSWORD = 'change_this'

# Email settings
EMAIL_FROM = 'change@email.nl',
