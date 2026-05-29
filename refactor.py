import os
import glob

replacements = [
    ("OpmProcessor", "OpmProcessor"),
    ("opm_processor", "opm_processor"),
    ("OPM-Acquisition", "OPM-Acquisition"),
    ("OPM Acquisition", "OPM Acquisition"),
    ("OPM ACQUISITION", "OPM ACQUISITION"),
    ("opm_recording_", "opm_recording_"),
    ("opm_export_", "opm_export_"),
    ('group_name="OPM"', 'group_name="OPM"'),
    ('group_name: str = "OPM"', 'group_name: str = "OPM"'),
    ('OPM_Acquisition', 'OPM_Acquisition'),
    ('OPM BAND', 'OPM BAND'),
    ('OPM data', 'OPM data'),
    ('OPM signal', 'OPM signal'),
    ('OPM 24-Channel', 'OPM 24-Channel'),
    ('OPM-like', 'OPM-like'),
    (' OPM ', ' OPM '),
    (' OPM.', ' OPM.'),
]

files = glob.glob("**/*.py", recursive=True)
for f in files:
    if ".venv" in f: continue
    
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        
    original = content
    for old, new in replacements:
        content = content.replace(old, new)
        
    if content != original:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated {f}")
