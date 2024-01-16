"""Clarity Portal configuration."""

# Website
SECRET_KEY = 'change_this'
REMOVED_SAMPLES_FILE = 'path/to/removed_samples.txt'
SAMPLE_NAME_FORBIDDEN = [' ', '_', ',', '+']  # Forbidden characters in sample name
LIMS_INDICATIONS = {
    'PD-PMC001': {
        'project_name_prefix': 'PMC_DX_WES',
        'sample_name_prefixes': ['PM'],
        'workflow_id': '1252',  # Dx Sequence facility v1.6
        'email_to': [],
    },
    'PD-PMC002': {
        'project_name_prefix': 'PMC_DX_WGS',
        'sample_name_prefixes': ['PM'],
        'workflow_id': '1252',  # Dx Sequence facility v1.6
        'email_to': [],
    },
    'RNA_seq': {
        'project_name_prefix': 'DX_RNASeq',
        'sample_name_prefixes': ['U','2'],
        'workflow_id': '1252',  # Dx Sequence facility v1.6
        'email_to': [],
    },
    'NEF00': {
        'project_name_prefix': 'DX',
        'sample_name_prefixes': ['U'],
        'workflow_id': '1252',  # Dx Sequence facility v1.6
        'email_to': [],
    },
    'ONB01': {
        'project_name_prefix': 'DX_GIAB',
        'sample_name_prefixes': ['GIAB'],
        'workflow_id': '1252',  # Dx Sequence facility v1.6
        'email_to': [],
    },
    'WGS': {
        'project_name_prefix': 'DX_WGS',
        'sample_name_prefixes': [''],
        'workflow_id': '1252',  # Dx Sequence facility v1.6
        'email_to': [],
    },
    'WGS_titr': {
        'project_name_prefix': 'DX_WGS_titr',
        'sample_name_prefixes': [''],
        'workflow_id': '1252', # Dx Sequence facility v1.6
        'email_to': [],
    },
    'DxVal': {
        'project_name_prefix': 'DxVal',
        'sample_name_prefixes': [''],
        'workflow_id': '1252',  # Dx Sequence facility v1.6
        'email_to': [],
    },
    'DxExtern': {
        'project_name_prefix': 'DxExtern',
        'sample_name_prefixes': [''],
        'workflow_id': '1252',  # Dx Sequence facility v1.6
        'email_to': [],
    },
    'CDL': {
        'project_name_prefix': 'Dx_CDL',
        'sample_name_prefixes': [''],
        'workflow_id': '1252',  # Dx Sequence facility v1.6
        'email_to': [],
    },
    'USEQ': {
        'project_name_prefix': 'Dx_USEQ',
        'sample_name_prefixes': [''],
        'workflow_id': '1252',  # Dx Sequence facility v1.6
        'email_to': [],
    },

}

LIMS_DX_SAMPLE_SUBMIT_WORKFLOW = '1252'  # Dx Sequence facility v1.6

# Genologics
BASEURI = 'change_this'
USERNAME = 'change_this'
PASSWORD = 'change_this'

# Email settings
EMAIL_FROM = 'change@email.nl',
