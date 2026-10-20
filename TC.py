# -*- coding: utf-8 -*-
import os
from nicegui import ui, app
import json

# --- SPECIFICATION BASELINE DATA TABLES ---
MODEL_BASE_DURATIONS = {
    "Model 4x": 8.5,
    "Model 5x": 9.0,
    "Model 8x": 9.5
}

UPGRADE_PATHS = {
    "2.6.0-2.7.2": ["2.7.2"],
    "2.6.0-2.7.7": ["2.7.2", "2.7.7"],
    "2.6.0-2.7.9": ["2.7.2", "2.7.7", "2.7.9"],
    "2.7.2-2.7.7": ["2.7.7"],
    "2.7.7-2.7.9": ["2.7.9"]
}

PACKAGE_DATABASE = [
    {"id": "PKG001", "type": "IDPA OE", "version": "2.7.2", "filename": "idpa-hw-upgrade-2.7.2-example.tar.gz", "size": "61 GB", "sha256": "EXAMPLE_SHA256_272", "download": "https://example.com/download/idpa-2.7.2", "applicableFor": "2.7.2"},
    {"id": "PKG002", "type": "NDMP", "version": "19.4", "filename": "ndmp-upgrade-19.4-example.zip", "size": "2 GB", "sha256": "EXAMPLE_SHA256_NDMP194", "download": "https://example.com/download/ndmp-19.4", "applicableFor": "NDMP for 2.7.2"},
    {"id": "PKG003", "type": "IDPA OE", "version": "2.7.7", "filename": "idpa-hw-upgrade-2.7.7-example.tar.gz", "size": "62 GB", "sha256": "EXAMPLE_SHA256_277", "download": "https://example.com/download/idpa-2.7.7", "applicableFor": "2.7.7"},
    {"id": "PKG004", "type": "NDMP", "version": "19.10", "filename": "ndmp-upgrade-19.10-example.zip", "size": "2 GB", "sha256": "EXAMPLE_SHA256_NDMP1910", "download": "https://example.com/download/ndmp-19.10", "applicableFor": "NDMP for 2.7.7"},
    {"id": "PKG005", "type": "IDPA OE", "version": "2.7.9", "filename": "idpa-hw-upgrade-2.7.9-example.tar.gz", "size": "62 GB", "sha256": "EXAMPLE_SHA256_279", "download": "https://example.com/download/idpa-2.7.9", "applicableFor": "2.7.9"},
    {"id": "PKG006", "type": "NDMP", "version": "19.12", "filename": "ndmp-upgrade-19.12-example.zip", "size": "2 GB", "sha256": "EXAMPLE_SHA256_NDMP1912", "download": "https://example.com/download/ndmp-19.12", "applicableFor": "NDMP for 2.7.9"},
    {"id": "PKG007", "type": "Hotfix", "version": "338905", "filename": "hotfix-338905-example.zip", "size": "1 GB", "sha256": "EXAMPLE_SHA256_HF338905", "download": "https://example.com/download/hotfix-338905", "applicableFor": "2.7.7"},
    {"id": "PKG008", "type": "Hotfix", "version": "338913", "filename": "hotfix-338913-example.zip", "size": "1 GB", "sha256": "EXAMPLE_SHA256_HF338913", "download": "https://example.com/download/hotfix-338913", "applicableFor": "2.7.9"},
    {"id": "PKG009", "type": "DDOS", "version": "8.3.1.45", "filename": "ddos-upgrade-8.3.1.45-example.rpm", "size": "5 GB", "sha256": "EXAMPLE_SHA256_DDOS83145", "download": "https://example.com/download/ddos-8.3.1.45", "applicableFor": "After 2.7.9"},
    {"id": "PKG010", "type": "AVE /space", "version": "19.4.0-7", "filename": "ave_scale-19.4.0-7.zip", "size": "10 GB", "sha256": "EXAMPLE_SHA256_AVESPACE", "download": "https://example.com/download/ave-space-upgrade", "applicableFor": "2.7.2"}
]

REF_DOCUMENTS = [
    {"name": "Upgrade Preparation Guide", "url": "https://example.com/docs/upgrade-preparation-guide"},
    {"name": "Release Notes", "url": "https://example.com/docs/release-notes"},
    {"name": "Compatibility Guide", "url": "https://example.com/docs/compatibility-guide"},
    {"name": "Recommended Code Matrix", "url": "https://example.com/docs/recommended-code-matrix"},
    {"name": "RPS Upgrade FAQ", "url": "https://example.com/docs/rps-upgrade-faq"}
]

activity_rows = []

# --- UI HEADER ---
with ui.header().classes('bg-blue-900 text-white items-center justify-between p-4 shadow-md'):
    with ui.row().classes('items-center gap-2'):
        ui.icon('build', size='md')
        ui.label('PowerProtect DP — Technical Consultation (TC) Portal').classes('text-xl font-bold')
    ui.chip('Spec v1.0 Compliant', color='blue-6').classes('text-white')

# --- MAIN FORM LAYOUT ---
with ui.row().classes('w-full p-6 gap-6'):

    # LEFT COLUMN: INPUT CONTROLS
    with ui.column().classes('flex-1 gap-6'):

        with ui.card().classes('w-full p-5 border-l-4 border-blue-600 shadow-sm'):
            ui.label('1. Customer & System Details').classes('text-md font-bold text-blue-900 mb-2')
            with ui.grid(columns=2).classes('w-full gap-3'):
                cust_name = ui.input('Customer Name *', value='').classes('w-full')
                cust_loc = ui.input('Customer Site / Location *', value='').classes('w-full')
                sr_num = ui.input('Upgrade SR *', value='').classes('w-full')
                serial_num = ui.input('Serial Number *', value='').classes('w-full')
                sys_model = ui.select(['NA', 'Model 4x', 'Model 5x', 'Model 8x'], label='System Model *', value='NA').classes('w-full')
                curr_code = ui.select(['NA', '2.6.0', '2.7.2', '2.7.7', '2.7.9'], label='Current Code *', value='NA').classes('w-full')
                req_code = ui.select(['NA', '2.6.0', '2.7.2', '2.7.7', '2.7.9'], label='Code Requested *', value='NA').classes('w-full')
                rec_code = ui.select(['NA', '2.6.0', '2.7.2', '2.7.7', '2.7.9'], label='Code Recommended *', value='NA').classes('w-full')
                conf_code = ui.select(['NA', '2.6.0', '2.7.2', '2.7.7', '2.7.9'], label='Code Confirmed *', value='NA').classes('w-full')
            
            upg_notes = ui.input('Upgrade Request Notes', value='').classes('w-full mt-2')

        with ui.card().classes('w-full p-5 border-l-4 border-teal-600 shadow-sm'):
            ui.label('2. System Health Checks').classes('text-md font-bold text-teal-900 mb-2')
            with ui.grid(columns=2).classes('w-full gap-3'):
                acm_dashboard = ui.select(['Good', 'Issues found - remediated', 'Issues found - outstanding'], label='ACM Dashboard Status *', value='Good').classes('w-full')
                pdf_status = ui.select([
                    'Good — downloaded and attached to SR (Prefixed with Tech Consult)',
                    'Issue — PDF download fails; all other health checks pass; retest post-upgrade and raise support ticket if needed'
                ], label='PDF Status *', value='Good — downloaded and attached to SR (Prefixed with Tech Consult)').classes('w-full')
                ruck_status = ui.select(['Good', 'Issues remediated', 'Issues pending'], label='RUCK Status *', value='Good').classes('w-full')
                acm_snapshot = ui.select([
                    'No VM Snapshot discovered',
                    'VM Snapshot discovered — customer confirmed removal before upgrade using KB 000218806',
                    'Removal pending'
                ], label='ACM VM Snapshot *', value='No VM Snapshot discovered').classes('w-full')
                validation_status = ui.select([
                    'Code Downloaded and Validation Passed',
                    'Downloaded but validation not run',
                    'Downloaded and validation failed',
                    'Code not downloaded'
                ], label='Validation Status *', value='Code Downloaded and Validation Passed').classes('w-full')
                idrac_status = ui.select(['Configured and Accessible', 'Configured but Not Accessible', 'Not Configured'], label='iDRAC Status *', value='Configured and Accessible').classes('w-full')
                exceptional_tasks = ui.select(['No Action Required', 'Review RCM Activity Notes', 'Action Required'], label='Exceptional Tasks *', value='No Action Required').classes('w-full')
                health_status = ui.select([
                    'IDPA is healthy and ready for upgrade — No issues found. Proceed as scheduled.',
                    'IDPA is healthy and ready for upgrade — Issues found were remediated or are not upgrade-related. Proceed as scheduled.',
                    'IDPA is not healthy for upgrade — Issues identified with associated remediation plan.'
                ], label='Overall Upgrade Health Status *', value='IDPA is healthy and ready for upgrade — No issues found. Proceed as scheduled.').classes('w-full')

        with ui.card().classes('w-full p-5 border-l-4 border-indigo-600 shadow-sm'):
            ui.label('3. Upgrade Preparation Inputs').classes('text-md font-bold text-indigo-900 mb-2')
            with ui.grid(columns=3).classes('w-full gap-3'):
                upg_review = ui.select([
                    'Customer has already reviewed the UPG, and did not have any further questions',
                    'Customer has already reviewed the UPG, and I have addressed the follow-up questions',
                    'Customer has not reviewed the UPG'
                ], label='UPG Review *', value='Customer has already reviewed the UPG, and did not have any further questions').classes('w-full')
                prereqs_status = ui.select([
                    'Customer meets upgrade requirements and acknowledged prerequisites',
                    'Customer does not meet requirements/prerequisites',
                    'Requirements review pending'
                ], label='Prerequisites Status *', value='Customer meets upgrade requirements and acknowledged prerequisites').classes('w-full')
                download_status = ui.select([
                    'Code downloaded and ready',
                    'Customer will follow instructions in pre-check report email',
                    'Already downloaded; customer will upload prior to upgrade',
                    'Code not downloaded'
                ], label='Code Download Status *', value='Code downloaded and ready').classes('w-full')

        with ui.card().classes('w-full p-5 border-l-4 border-amber-600 shadow-sm'):
            ui.label('4. RCM Schedule & Activities').classes('text-md font-bold text-amber-900 mb-2')
            
            activity_container = ui.column().classes('w-full gap-3')

            def add_activity_card(rcm='TBD', name='IDPA OE Code Upgrade + NDMP Upgrade', from_v='NA', to_v='NA', sched='TBD', ndmp=True, ddos=False, hf=False, ave=False):
                with activity_container:
                    card = ui.card().classes('w-full p-3 bg-gray-50 border border-gray-200')
                    with card:
                        with ui.row().classes('w-full justify-between items-center mb-1'):
                            ui.label('Activity Step Input').classes('font-bold text-xs text-gray-700')
                            ui.button(icon='delete', color='negative', on_click=lambda: remove_activity_card(card_data)).props('flat round dense')
                        
                        with ui.grid(columns=3).classes('w-full gap-2'):
                            inp_rcm = ui.input('RCM ID', value=rcm).classes('w-full text-xs')
                            inp_name = ui.input('Activity Name', value=name).classes('w-full text-xs')
                            inp_sched = ui.input('Scheduled Date/Time', value=sched).classes('w-full text-xs')
                            inp_from = ui.select(['NA', '2.6.0', '2.7.2', '2.7.7', '2.7.9'], label='From Version', value=from_v).classes('w-full text-xs')
                            inp_to = ui.select(['NA', '2.6.0', '2.7.2', '2.7.7', '2.7.9'], label='To Version', value=to_v).classes('w-full text-xs')
                        
                        with ui.row().classes('w-full gap-4 mt-2'):
                            chk_ndmp = ui.checkbox('NDMP', value=ndmp)
                            chk_ddos = ui.checkbox('DDOS Upgrade', value=ddos)
                            chk_hf = ui.checkbox('Hotfix', value=hf)
                            chk_ave = ui.checkbox('AVE /space', value=ave)

                        card_data = {
                            'card_widget': card,
                            'rcm': inp_rcm, 'name': inp_name, 'sched': inp_sched,
                            'from': inp_from, 'to': inp_to,
                            'ndmp': chk_ndmp, 'ddos': chk_ddos, 'hf': chk_hf, 'ave': chk_ave
                        }
                        activity_rows.append(card_data)

            def remove_activity_card(card_data):
                activity_container.remove(card_data['card_widget'])
                activity_rows.remove(card_data)

            ui.button('+ Add Upgrade Step', on_click=lambda: add_activity_card()).classes('bg-amber-700 text-white text-xs')

        with ui.card().classes('w-full p-5 border-l-4 border-purple-600 shadow-sm'):
            ui.label('5. Scheduling Actions').classes('text-md font-bold text-purple-900 mb-2')
            scheduling_action = ui.select([
                'No issues; no further scheduling required - Reserved slot converted',
                'Requires rescheduling Tech Consult after issues are resolved - Reserved slot not converted',
                'Issues found but not upgrade-blocking - Reserved slot converted',
                'Upgrade-blocking issues found; must be resolved before upgrade - Reserved slot converted'
            ], label='Action Taken *', value='No issues; no further scheduling required - Reserved slot converted').classes('w-full')

        ui.button('⚡ Generate Deliverables', on_click=lambda: process_tc_generation()).classes('w-full bg-blue-700 text-white font-bold p-3 text-base shadow-md')

    # RIGHT COLUMN: OUTPUT PREVIEW & DOWNLOAD OPTIONS
    with ui.column().classes('flex-1 gap-6'):
        
        with ui.card().classes('w-full p-5 border-l-4 border-emerald-600 shadow-sm'):
            ui.label('Internal SR Output Template').classes('text-md font-bold text-emerald-900 mb-2')
            sr_text_output = ui.textarea().classes('w-full font-mono text-xs').props('rows=14 readonly')
            
            with ui.row().classes('w-full gap-2 mt-2'):
                ui.button('📋 Copy SR Template', on_click=lambda: copy_to_clipboard(sr_text_output.value)).classes('bg-emerald-700 text-white')
                ui.button('💾 Download SR Output (.txt)', on_click=lambda: download_file(sr_text_output.value, f"{sr_num.value or 'TC'}_SR_Summary.txt")).classes('bg-emerald-900 text-white')

        with ui.card().classes('w-full p-5 border-l-4 border-sky-600 shadow-sm'):
            ui.label('Customer Email Preview').classes('text-md font-bold text-sky-900 mb-2')
            email_subject_output = ui.input('Subject Line').classes('w-full font-bold mb-2').props('readonly')
            email_body_output = ui.textarea().classes('w-full font-mono text-xs').props('rows=14 readonly')
            
            with ui.row().classes('w-full gap-2 mt-2'):
                ui.button('📋 Copy Email Text', on_click=lambda: copy_to_clipboard(email_body_output.value)).classes('bg-sky-700 text-white')
                ui.button('💾 Download Email (.txt)', on_click=lambda: download_file(email_body_output.value, f"{sr_num.value or 'TC'}_Customer_Email.txt")).classes('bg-sky-900 text-white')


# --- PROCESSING & FILE DOWNLOAD LOGIC ---
def process_tc_generation():
    path_key = f"{curr_code.value}-{conf_code.value}"
    target_steps = UPGRADE_PATHS.get(path_key, [conf_code.value] if conf_code.value != 'NA' else [])
    upgrade_path_str = " → ".join([curr_code.value] + target_steps) if curr_code.value != 'NA' else 'NA'

    base_oe_hours = MODEL_BASE_DURATIONS.get(sys_model.value, 9.0)

    required_packages = []
    internal_act_lines = []
    customer_act_lines = []

    for row in activity_rows:
        act_from = row['from'].value
        act_to = row['to'].value
        act_rcm = row['rcm'].value if row['rcm'].value else "TBD"
        act_date = row['sched'].value if row['sched'].value else "TBD"
        act_name = row['name'].value

        has_ndmp = row['ndmp'].value
        has_ddos = row['ddos'].value
        has_hf = row['hf'].value
        has_ave = row['ave'].value

        ndmp_hrs = 0.5 if has_ndmp else 0.0
        ddos_hrs = 3.0 if has_ddos else 0.0
        hf_hrs = 1.0 if has_hf else 0.0
        ave_hrs = 1.0 if has_ave else 0.0
        
        internal_planned_duration = base_oe_hours + ndmp_hrs + ddos_hrs + hf_hrs + ave_hrs + 1.0

        internal_act_lines.append(
            f"{act_rcm} | {act_name} | {act_from} → {act_to} | {act_date} | Planned Duration: {internal_planned_duration} Hours (Internal)"
        )
        customer_act_lines.append(
            f"{act_rcm} | {act_name} | {act_from} → {act_to} | {act_date}"
        )

        if act_to != 'NA':
            oe_pkg = next((p for p in PACKAGE_DATABASE if p["type"] == "IDPA OE" and p["version"] == act_to), None)
            if oe_pkg: required_packages.append(oe_pkg)

            if has_ndmp:
                ndmp_pkg = next((p for p in PACKAGE_DATABASE if p["type"] == "NDMP" and p["applicableFor"] == f"NDMP for {act_to}"), None)
                if ndmp_pkg: required_packages.append(ndmp_pkg)

            if has_hf:
                hf_pkg = next((p for p in PACKAGE_DATABASE if p["type"] == "Hotfix" and p["applicableFor"] == act_to), None)
                if hf_pkg: required_packages.append(hf_pkg)

            if has_ave and act_to == "2.7.2":
                ave_pkg = next((p for p in PACKAGE_DATABASE if p["type"] == "AVE /space"), None)
                if ave_pkg: required_packages.append(ave_pkg)

            if has_ddos:
                ddos_pkg = next((p for p in PACKAGE_DATABASE if p["type"] == "DDOS"), None)
                if ddos_pkg: required_packages.append(ddos_pkg)

    seen_ids = set()
    unique_packages = []
    for pkg in required_packages:
        if pkg["id"] not in seen_ids:
            seen_ids.add(pkg["id"])
            unique_packages.append(pkg)

    sr_template = f"""*** POWERPROTECT DP TECHNICAL CONSULTATION (TC) SUMMARY ***

1. CUSTOMER & SYSTEM DETAILS
Customer Name: {cust_name.value}
Customer Site / Location: {cust_loc.value}
Upgrade SR: {sr_num.value}
PowerProtect DP Serial Number: {serial_num.value}
System Model: {sys_model.value}
Current Code: {curr_code.value}
Code Requested: {req_code.value}
Code Recommended: {rec_code.value}
Code Confirmed: {conf_code.value}
Upgrade Request Notes: {upg_notes.value}

2. SYSTEM HEALTH & PREPARATION
ACM Dashboard Status: {acm_dashboard.value}
PDF Status: {pdf_status.value}
RUCK Status: {ruck_status.value}
ACM VM Snapshot: {acm_snapshot.value}
Validation Status: {validation_status.value}
iDRAC Status: {idrac_status.value}
Exceptional Tasks: {exceptional_tasks.value}
Upgrade Health Status: {health_status.value}

3. UPGRADE PREPARATION STATUS
UPG Review: {upg_review.value}
Prerequisites: {prereqs_status.value}
Code Stage: {download_status.value}

4. UPGRADE PATH & SCHEDULE
Upgrade Path: {upgrade_path_str}

RCM SCHEDULE & ACTIVITIES:
""" + "\n".join(internal_act_lines) + f"""

5. SCHEDULING ACTION
Action Taken: {scheduling_action.value}"""

    customer_pkg_rows = [
        f"{p['type']} | {p['version']} | {p['filename']} | {p['size']} | {p['sha256']} | {p['version']} ({p['download']})"
        for p in unique_packages
    ]
    
    docs_formatted = "\n".join([f"{d['name']} ({d['url']})" for d in REF_DOCUMENTS])

    customer_email_body = f"""#TechConsult

Hello {cust_name.value or 'Customer'},

I have completed the technical consultation and pre-checks for your PowerProtect DP upgrade.

CUSTOMER ACTION SUMMARY

Required:
- Download required upgrade package(s).
- Upload packages to the PowerProtect DP system.
- Verify package checksum.
- Review Release Notes and complete prerequisites.
- Resolve upgrade-blocking issues.
- Disable backup policies before the applicable upgrade activity.

Recommended:
- Review the Upgrade Preparation Guide.
- Verify compatibility and upgrade requirements.
- Ensure business continuity.

TECHNICAL CONSULTATION DETAILS
Customer Name: {cust_name.value}
Customer Site / Location: {cust_loc.value}
Upgrade SR: {sr_num.value}
PowerProtect DP Serial Number: {serial_num.value}
System Model: {sys_model.value}
Current Code: {curr_code.value}
Code Requested: {req_code.value}
Code Recommended: {rec_code.value}
Code Confirmed: {conf_code.value}

OVERALL HEALTH STATUS
{health_status.value}

UPGRADE PATH
{upgrade_path_str}

UPGRADE STEPS
""" + "\n".join(customer_act_lines) + f"""

UPGRADE PACKAGES
Package Type | Version | Filename | Size | SHA256SUM | Download
""" + "\n".join(customer_pkg_rows) + f"""

REFERENCE DOCUMENTS
{docs_formatted}

DELL / SUPPORT RESPONSIBILITIES
- Review system health and validate the upgrade path.
- Perform applicable pre-checks.
- Execute the upgrade according to the agreed plan.
- Perform post-upgrade validation.

CUSTOMER RESPONSIBILITIES
- Download and stage required software.
- Verify package checksums.
- Review the Upgrade Preparation Guide and Release Notes.
- Complete prerequisites and compatibility checks.
- Disable backup policies before the applicable activity.
- Complete required client/proxy/plugin updates after the upgrade.
- Resolve upgrade-blocking issues before the applicable activity.

Thank you,
Dell Technologies Support"""

    sr_text_output.value = sr_template
    email_subject_output.value = f"PowerProtect DP Upgrade Technical Consultation & Schedule — {sr_num.value or 'SR'}"
    email_body_output.value = customer_email_body

    ui.notify('Technical Consultation Output Generated Successfully!', type='positive')

def copy_to_clipboard(text_val):
    ui.run_javascript(f'navigator.clipboard.writeText({json.dumps(text_val)})')
    ui.notify('Copied to Clipboard!', type='info')

def download_file(content, filename):
    if not content:
        ui.notify('Please generate deliverables first!', type='warning')
        return
    ui.download(content.encode('utf-8'), filename)
    ui.notify(f'Downloading {filename}...', type='positive')

# --- ENVIRONMENT PORT BINDING FOR RENDER / LOCAL ---
port = int(os.environ.get("PORT", 8080))

ui.run(
    title="Technical Consultation Portal",
    host="0.0.0.0",
    port=port,
    reload=False
)