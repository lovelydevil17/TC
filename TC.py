# -*- coding: utf-8 -*-
import os
from datetime import datetime
from nicegui import ui, app
import json

# --- SPECIFICATION BASELINE DATA TABLES ---
MODEL_BASE_DURATIONS = {
    "Model 4x": 8.5,
    "Model 5x": 9.0,
    "Model 8x": 9.5
}

UPGRADE_PATHS = {
    "2.6.0": ["2.7.2", "2.7.7", "2.7.9"],
    "2.7.2": ["2.7.7", "2.7.9"],
    "2.7.7": ["2.7.9"],
    "2.7.9": ["DDOS Upgrade", "Hotfix Upgrade"]
}

AUTO_NEXT_VERSION = {
    "2.6.0": "2.7.2",
    "2.7.2": "2.7.7",
    "2.7.7": "2.7.9",
    "2.7.9": "DDOS Upgrade"
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

# --- CORE AUTO DURATION CALCULATION HELPER ---
def compute_raw_duration(model_str, base_name, ndmp_cnt, add_acts):
    if model_str == 'NA':
        return 0.0
        
    raw_duration_hrs = 0.0
    if base_name in ['IDPA OE Code Upgrade', 'NA']:
        raw_duration_hrs += MODEL_BASE_DURATIONS.get(model_str, 0.0)
    elif base_name == 'DDOS Upgrade':
        raw_duration_hrs += 3.0
    elif base_name == 'Hotfix Upgrade':
        raw_duration_hrs += 1.0

    ndmp_multiplier_map = {'Yes—1': 1, 'Yes—2': 2, 'Yes—3': 3, 'Yes—4': 4}
    if ndmp_cnt in ndmp_multiplier_map:
        raw_duration_hrs += ndmp_multiplier_map[ndmp_cnt] * 0.5
    elif ndmp_cnt == 'Yes—Other':
        raw_duration_hrs += 0.5

    if 'DDOS Upgrade' in add_acts and base_name != 'DDOS Upgrade':
        raw_duration_hrs += 3.0
    if 'Hotfix Upgrade' in add_acts and base_name != 'Hotfix Upgrade':
        raw_duration_hrs += 1.0
    if 'AVE /space expansion' in add_acts:
        raw_duration_hrs += 1.0

    return raw_duration_hrs

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

        # SECTION 1: CUSTOMER & SYSTEM DETAILS
        with ui.card().classes('w-full p-5 border-l-4 border-blue-600 shadow-sm'):
            ui.label('1. Customer & System Details').classes('text-md font-bold text-blue-900 mb-2')
            
            code_selection_options = [
                'NA', 
                '2.6.0', 
                '2.7.2', 
                '2.7.7', 
                '2.7.9', 
                'DDOS Upgrade', 
                'Hotfix Upgrade',
                'Other'
            ]

            with ui.grid(columns=2).classes('w-full gap-3'):
                cust_name = ui.input('Customer Name *', value='').classes('w-full')
                cust_loc = ui.input('Customer Site / Location *', value='').classes('w-full')
                sr_num = ui.input('Upgrade SR *', value='').classes('w-full')
                serial_num = ui.input('Serial Number *', value='').classes('w-full')
                
                with ui.column().classes('w-full gap-1'):
                    sys_model = ui.select(['NA', 'Model 4x', 'Model 5x', 'Model 8x', 'Other'], label='IDPA Model *', value='NA').classes('w-full')
                    sys_model_other = ui.input('Specify IDPA Model Details', value='').classes('w-full text-xs')
                    sys_model_other.bind_visibility_from(sys_model, 'value', backward=lambda v: str(v) == 'Other')

                with ui.column().classes('w-full gap-1'):
                    curr_code = ui.select(code_selection_options, label='Current Code *', value='NA').classes('w-full')
                    curr_code_other = ui.input('Specify Current Code Details', value='').classes('w-full text-xs')
                    curr_code_other.bind_visibility_from(curr_code, 'value', backward=lambda v: str(v) == 'Other')

                with ui.column().classes('w-full gap-1'):
                    req_code = ui.select(code_selection_options, label='Code Requested *', value='NA').classes('w-full')
                    req_code_other = ui.input('Specify Code Requested Details', value='').classes('w-full text-xs')
                    req_code_other.bind_visibility_from(req_code, 'value', backward=lambda v: str(v) == 'Other')

                with ui.column().classes('w-full gap-1'):
                    rec_code = ui.select(code_selection_options, label='Code Recommended *', value='NA').classes('w-full')
                    rec_code_other = ui.input('Specify Code Recommended Details', value='').classes('w-full text-xs')
                    rec_code_other.bind_visibility_from(rec_code, 'value', backward=lambda v: str(v) == 'Other')

                with ui.column().classes('w-full gap-1'):
                    conf_code = ui.select(code_selection_options, label='Code Confirmed *', value='NA').classes('w-full')
                    conf_code_other = ui.input('Specify Code Confirmed Details', value='').classes('w-full text-xs')
                    conf_code_other.bind_visibility_from(conf_code, 'value', backward=lambda v: str(v) == 'Other')
            
            upg_notes = ui.input('Upgrade Request Notes', value='').classes('w-full mt-2')

        # SECTION 2: SYSTEM HEALTH CHECKS
        with ui.card().classes('w-full p-5 border-l-4 border-teal-600 shadow-sm'):
            ui.label('2. System Health Checks').classes('text-md font-bold text-teal-900 mb-2')
            with ui.grid(columns=2).classes('w-full gap-3'):
                with ui.column().classes('w-full gap-1'):
                    acm_dashboard = ui.select(['NA', 'Good', 'Issues found - remediated', 'Issues found - outstanding', 'Other'], label='ACM Dashboard Status *', value='NA').classes('w-full')
                    acm_details = ui.input('ACM Issue / Other Details', value='').classes('w-full text-xs')
                    acm_details.bind_visibility_from(acm_dashboard, 'value', backward=lambda v: 'Issues' in str(v) or str(v) == 'Other')

                with ui.column().classes('w-full gap-1'):
                    ruck_status = ui.select(['NA', 'Good', 'Issues remediated', 'Issues pending', 'Other'], label='RUCK Status *', value='NA').classes('w-full')
                    ruck_details = ui.input('RUCK Issue / Other Details', value='').classes('w-full text-xs')
                    ruck_details.bind_visibility_from(ruck_status, 'value', backward=lambda v: 'Issues' in str(v) or str(v) == 'Other')

                with ui.column().classes('w-full gap-1'):
                    pdf_status = ui.select([
                        'NA',
                        'Good — downloaded and attached to SR (Prefixed with Tech Consult)',
                        'Issue — PDF download fails; all other health checks pass; retest post-upgrade and raise support ticket if needed',
                        'Other'
                    ], label='PDF Status *', value='NA').classes('w-full')
                    pdf_other = ui.input('Specify PDF Status Details', value='').classes('w-full text-xs')
                    pdf_other.bind_visibility_from(pdf_status, 'value', backward=lambda v: str(v) == 'Other')
                
                with ui.column().classes('w-full gap-1'):
                    acm_snapshot = ui.select([
                        'NA',
                        'No VM Snapshot discovered',
                        'VM Snapshot discovered — customer confirmed removal before upgrade using KB 000218806',
                        'Removal pending',
                        'Other'
                    ], label='ACM VM Snapshot *', value='NA').classes('w-full')
                    acm_snap_other = ui.input('Specify ACM Snapshot Details', value='').classes('w-full text-xs')
                    acm_snap_other.bind_visibility_from(acm_snapshot, 'value', backward=lambda v: str(v) == 'Other')
                
                with ui.column().classes('w-full gap-1'):
                    validation_status = ui.select([
                        'NA',
                        'Code Downloaded and Validation Passed',
                        'Downloaded but validation not run',
                        'Downloaded and validation failed',
                        'Code not downloaded',
                        'Other'
                    ], label='Validation Status *', value='NA').classes('w-full')
                    val_stat_other = ui.input('Specify Validation Status Details', value='').classes('w-full text-xs')
                    val_stat_other.bind_visibility_from(validation_status, 'value', backward=lambda v: str(v) == 'Other')
                
                with ui.column().classes('w-full gap-1'):
                    idrac_status = ui.select(['NA', 'Configured and Accessible', 'Configured but Not Accessible', 'Not Configured', 'Other'], label='iDRAC Status *', value='NA').classes('w-full')
                    idrac_other = ui.input('Specify iDRAC Status Details', value='').classes('w-full text-xs')
                    idrac_other.bind_visibility_from(idrac_status, 'value', backward=lambda v: str(v) == 'Other')

                with ui.column().classes('w-full gap-1'):
                    exceptional_tasks = ui.select(['NA', 'No Action Required', 'Review RCM Activity Notes', 'Action Required', 'Other'], label='Exceptional Tasks *', value='NA').classes('w-full')
                    exc_other = ui.input('Specify Exceptional Tasks Details', value='').classes('w-full text-xs')
                    exc_other.bind_visibility_from(exceptional_tasks, 'value', backward=lambda v: str(v) == 'Other')
                
                with ui.column().classes('w-full gap-1 col-span-2'):
                    health_status = ui.select([
                        'NA',
                        'IDPA is healthy and ready for upgrade — No issues found. Proceed as scheduled.',
                        'IDPA is healthy and ready for upgrade — Issues found were remediated or are not upgrade-related. Proceed as scheduled.',
                        'IDPA is not healthy for upgrade — Issues identified with associated remediation plan.',
                        'Other'
                    ], label='Overall Upgrade Health Status *', value='NA').classes('w-full')
                    health_issue_details = ui.input('Health Issue / Remediation Plan / Other Details', value='').classes('w-full text-xs')
                    health_issue_details.bind_visibility_from(health_status, 'value', backward=lambda v: 'not healthy' in str(v) or str(v) == 'Other')

        # SECTION 3: UPGRADE PREPARATION INPUTS
        with ui.card().classes('w-full p-5 border-l-4 border-indigo-600 shadow-sm'):
            ui.label('3. Upgrade Preparation Inputs').classes('text-md font-bold text-indigo-900 mb-2')
            with ui.grid(columns=3).classes('w-full gap-3'):
                with ui.column().classes('w-full gap-1'):
                    upg_review = ui.select([
                        'NA',
                        'Customer has already reviewed the UPG, and did not have any further questions',
                        'Customer has already reviewed the UPG, and I have addressed the follow-up questions',
                        'Customer has not reviewed the UPG',
                        'Other'
                    ], label='UPG Review *', value='NA').classes('w-full')
                    upg_rev_other = ui.input('Specify UPG Review Details', value='').classes('w-full text-xs')
                    upg_rev_other.bind_visibility_from(upg_review, 'value', backward=lambda v: str(v) == 'Other')

                with ui.column().classes('w-full gap-1'):
                    prereqs_status = ui.select([
                        'NA',
                        'Customer meets upgrade requirements and acknowledged prerequisites',
                        'Customer does not meet requirements/prerequisites',
                        'Requirements review pending',
                        'Other'
                    ], label='Prerequisites Status *', value='NA').classes('w-full')
                    prereq_other = ui.input('Specify Prerequisites Details', value='').classes('w-full text-xs')
                    prereq_other.bind_visibility_from(prereqs_status, 'value', backward=lambda v: str(v) == 'Other')

                with ui.column().classes('w-full gap-1'):
                    download_status = ui.select([
                        'NA',
                        'Code downloaded and ready',
                        'Customer will follow instructions in pre-check report email',
                        'Already downloaded; customer will upload prior to upgrade',
                        'Code not downloaded',
                        'Other'
                    ], label='Code Download Status *', value='NA').classes('w-full')
                    dl_stat_other = ui.input('Specify Download Status Details', value='').classes('w-full text-xs')
                    dl_stat_other.bind_visibility_from(download_status, 'value', backward=lambda v: str(v) == 'Other')

        # SECTION 4: RCM SCHEDULE & ACTIVITIES
        with ui.card().classes('w-full p-5 border-l-4 border-amber-600 shadow-sm'):
            ui.label('4. RCM Schedule & Activities').classes('text-md font-bold text-amber-900 mb-2')
            
            activity_container = ui.column().classes('w-full gap-3')

            def add_activity_card(rcm='TBD', name='IDPA OE Code Upgrade', from_v='NA', to_v='NA', date_val='', time_val='10:00', schedule_status='To be Scheduled', ndmp_count='No', ndmp_details='', add_acts=['No Additional Activities'], add_act_details='', duration_val=None, multi_step=False):
                with activity_container:
                    card = ui.card().classes('w-full p-3 bg-gray-50 border border-gray-200')
                    with card:
                        with ui.row().classes('w-full justify-between items-center mb-1'):
                            ui.label('Activity Step Input').classes('font-bold text-xs text-gray-700')
                            ui.button(icon='delete', color='negative', on_click=lambda: remove_activity_card(card_data)).props('flat round dense')
                        
                        with ui.grid(columns=3).classes('w-full gap-2 items-center'):
                            inp_rcm = ui.input('RCM Activity ID', value=rcm).classes('w-full text-xs')
                            
                            with ui.column().classes('w-full gap-1'):
                                inp_name = ui.select([
                                    'NA',
                                    'IDPA OE Code Upgrade',
                                    'DDOS Upgrade',
                                    'Hotfix Upgrade',
                                    'Other'
                                ], label='Base Activity *', value=name).classes('w-full text-xs')
                                inp_name_other = ui.input('Specify Base Activity', value='').classes('w-full text-xs')
                                inp_name_other.bind_visibility_from(inp_name, 'value', backward=lambda v: str(v) == 'Other')

                            inp_sched_status = ui.select(['To be Scheduled', 'Scheduled'], label='Schedule Status *', value=schedule_status).classes('w-full text-xs')
                            
                            with ui.column().classes('w-full gap-1'):
                                inp_from = ui.select(['NA', '2.6.0', '2.7.2', '2.7.7', '2.7.9', 'Other'], label='Upgrading From', value=from_v).classes('w-full text-xs')
                                inp_from_other = ui.input('Specify Upgrading From', value='').classes('w-full text-xs')
                                inp_from_other.bind_visibility_from(inp_from, 'value', backward=lambda v: str(v) == 'Other')

                            def get_filtered_to_options(selected_from):
                                curr = curr_code.value if curr_code.value != 'NA' else selected_from
                                allowed = UPGRADE_PATHS.get(curr, ['2.7.2', '2.7.7', '2.7.9', 'DDOS Upgrade', 'Hotfix Upgrade'])
                                filtered = [opt for opt in allowed if opt != selected_from]
                                return ['NA'] + filtered + ['Other']

                            with ui.column().classes('w-full gap-1'):
                                inp_to = ui.select(get_filtered_to_options(from_v), label='Upgrading To', value=to_v).classes('w-full text-xs')
                                inp_to_other = ui.input('Specify Upgrading To', value='').classes('w-full text-xs')
                                inp_to_other.bind_visibility_from(inp_to, 'value', backward=lambda v: str(v) == 'Other')

                            duration_options = [0.0] + [round(x * 0.5, 1) for x in range(1, 25)]
                            
                            init_model = sys_model.value if sys_model.value != 'Other' and sys_model.value != 'NA' else 'NA'
                            init_auto_hrs = compute_raw_duration(init_model, name, ndmp_count, add_acts)
                            initial_duration = duration_val if duration_val is not None else init_auto_hrs

                            inp_duration = ui.select(duration_options, label='Duration (Hours - Auto/Override)', value=initial_duration).classes('w-full text-xs')

                            def update_auto_duration():
                                m_val = sys_model.value if sys_model.value != 'Other' and sys_model.value != 'NA' else 'NA'
                                b_val = inp_name.value
                                n_val = inp_ndmp_count.value
                                a_val = inp_add_acts.value if isinstance(inp_add_acts.value, list) else []
                                
                                auto_calc = compute_raw_duration(m_val, b_val, n_val, a_val)
                                if auto_calc in duration_options:
                                    inp_duration.value = auto_calc

                            inp_name.on('update:value', lambda _: update_auto_duration())
                            sys_model.on('update:value', lambda _: update_auto_duration())

                            def on_from_change(e):
                                new_from = e.value
                                inp_to.set_options(get_filtered_to_options(new_from))
                                if new_from in AUTO_NEXT_VERSION:
                                    inp_to.value = AUTO_NEXT_VERSION[new_from]

                            inp_from.on('update:value', on_from_change)
                            curr_code.on('update:value', lambda e: inp_to.set_options(get_filtered_to_options(inp_from.value)))

                            with ui.input('Scheduled Date', value=date_val).classes('w-full text-xs') as inp_date:
                                with inp_date.add_slot('append'):
                                    ui.icon('event').classes('cursor-pointer').on('click', lambda: date_menu.open())
                                with ui.menu() as date_menu:
                                    ui.date().bind_value(inp_date)

                            time_options = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
                            inp_time = ui.select(time_options, label='Time (24h)', value=time_val).classes('w-full text-xs')

                        with ui.row().classes('w-full gap-2 mt-2 items-center'):
                            inp_ndmp_count = ui.select(['No', 'Yes—1', 'Yes—2', 'Yes—3', 'Yes—4', 'Yes—Other'], label='NDMP Upgrade / Count', value=ndmp_count).classes('w-1/2 text-xs')
                            inp_ndmp_count.on('update:value', lambda _: update_auto_duration())

                            inp_ndmp_details = ui.input('NDMP Count Details', value=ndmp_details).classes('w-1/2 text-xs')
                            inp_ndmp_details.bind_visibility_from(inp_ndmp_count, 'value', backward=lambda v: v == 'Yes—Other')

                        with ui.row().classes('w-full gap-2 mt-2 items-center'):
                            inp_add_acts = ui.select([
                                'No Additional Activities', 
                                'AVE /space expansion', 
                                'NDMP Upgrade', 
                                'DDOS Upgrade', 
                                'Hotfix Upgrade',
                                'Other'
                            ], multiple=True, label='Additional Activities', value=add_acts).classes('w-1/2 text-xs')
                            inp_add_acts.on('update:value', lambda _: update_auto_duration())
                            
                            inp_add_act_details = ui.input('Additional Activity Details', value=add_act_details).classes('w-1/2 text-xs')
                            inp_add_act_details.bind_visibility_from(inp_add_acts, 'value', backward=lambda v: isinstance(v, list) and 'Other' in v)

                        with ui.row().classes('w-full gap-4 mt-2'):
                            chk_multistep = ui.checkbox('Multi-Step OE Upgrade', value=multi_step)

                        card_data = {
                            'card_widget': card,
                            'rcm': inp_rcm, 'name': inp_name, 'name_other': inp_name_other,
                            'schedule_status': inp_sched_status,
                            'date': inp_date, 'time': inp_time,
                            'from': inp_from, 'from_other': inp_from_other,
                            'to': inp_to, 'to_other': inp_to_other,
                            'duration': inp_duration,
                            'ndmp_count': inp_ndmp_count, 'ndmp_details': inp_ndmp_details,
                            'add_acts': inp_add_acts, 'add_act_details': inp_add_act_details,
                            'multi_step': chk_multistep
                        }
                        activity_rows.append(card_data)

            def remove_activity_card(card_data):
                activity_container.remove(card_data['card_widget'])
                activity_rows.remove(card_data)

            ui.button('+ Add Upgrade Step', on_click=lambda: add_activity_card()).classes('bg-amber-700 text-white text-xs')

        # SECTION 5: SCHEDULING ACTIONS
        with ui.card().classes('w-full p-5 border-l-4 border-purple-600 shadow-sm'):
            ui.label('5. Scheduling Actions').classes('text-md font-bold text-purple-900 mb-2')
            with ui.column().classes('w-full gap-1'):
                scheduling_action = ui.select([
                    'NA',
                    'No issues; no further scheduling required - Reserved slot converted',
                    'Requires rescheduling Tech Consult after issues are resolved - Reserved slot not converted',
                    'Issues found but not upgrade-blocking - Reserved slot converted',
                    'Upgrade-blocking issues found; must be resolved before upgrade - Reserved slot converted',
                    'Other'
                ], label='Action Taken *', value='NA').classes('w-full')
                sched_act_other = ui.input('Specify Action Taken Details', value='').classes('w-full text-xs')
                sched_act_other.bind_visibility_from(scheduling_action, 'value', backward=lambda v: str(v) == 'Other')

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
                ui.button('💾 Download Outlook Email (.eml)', on_click=lambda: download_eml_file(email_subject_output.value, email_body_output.value, f"{sr_num.value or 'TC'}_Customer_Email.eml")).classes('bg-sky-900 text-white')


# Add 1 initial activity step card by default
add_activity_card()


# --- DURATION CALCULATION LOGIC ---
def calculate_activity_duration(model_str, base_name, ndmp_cnt, add_acts, manual_duration):
    if manual_duration is not None and float(manual_duration) > 0.0:
        raw_duration_hrs = float(manual_duration)
    else:
        raw_duration_hrs = compute_raw_duration(model_str, base_name, ndmp_cnt, add_acts)

    cust_buffered_duration = raw_duration_hrs + 1.0 if raw_duration_hrs > 0 else 0.0
    internal_planned_duration = raw_duration_hrs + 1.0 if raw_duration_hrs > 0 else 0.0

    return raw_duration_hrs, cust_buffered_duration, internal_planned_duration


def compute_combined_activity_name(base_name, ndmp_cnt, add_acts):
    if base_name in ['NA', 'DDOS Upgrade', 'Hotfix Upgrade']:
        return base_name
    
    has_ave = 'AVE /space expansion' in add_acts
    has_ndmp = ndmp_cnt != 'No' or 'NDMP Upgrade' in add_acts
    has_ddos = 'DDOS Upgrade' in add_acts
    has_hf = 'Hotfix Upgrade' in add_acts

    parts = []
    if has_ave:
        parts.append("AVE /space")
    parts.append("IDPA OE Code Upgrade" if base_name != 'Other' else "Custom Activity")

    suffixes = []
    if has_ndmp:
        suffixes.append("NDMP Upgrade")
    if has_ddos:
        suffixes.append("DDOS Upgrade")
    if has_hf:
        suffixes.append("Hotfix Upgrade")

    combined = " + ".join(parts)
    if suffixes:
        combined += " + " + " + ".join(suffixes)
    return combined


# --- PROCESSING & FILE DOWNLOAD LOGIC ---
def process_tc_generation():
    get_val = lambda sel, oth: oth.value if sel.value == 'Other' and oth.value else sel.value

    model_val = get_val(sys_model, sys_model_other)
    curr_val = get_val(curr_code, curr_code_other)
    req_val = get_val(req_code, req_code_other)
    rec_val = get_val(rec_code, rec_code_other)
    conf_val = get_val(conf_code, conf_code_other)

    upgrade_path_str = f"{curr_val} → {conf_val}" if curr_val != 'NA' and conf_val != 'NA' else 'NA'

    required_packages = []
    internal_act_lines = []
    customer_act_sections = []

    last_scheduled_dt = None

    for idx, row in enumerate(activity_rows, 1):
        act_from = get_val(row['from'], row['from_other'])
        act_to = get_val(row['to'], row['to_other'])
        sched_status = row['schedule_status'].value
        
        date_part = row['date'].value if row['date'].value else ""
        time_part = row['time'].value if row['time'].value else ""
        
        if sched_status == 'Scheduled' and date_part and time_part:
            act_rcm = row['rcm'].value if row['rcm'].value else "TBD"
            act_date = f"{date_part} {time_part}".strip()
            
            try:
                current_dt = datetime.strptime(f"{date_part} {time_part}", "%Y/%m/%d %H:%M")
            except ValueError:
                try:
                    current_dt = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
                except ValueError:
                    current_dt = None

            if current_dt and last_scheduled_dt:
                time_diff = (current_dt - last_scheduled_dt).total_seconds() / 3600.0
                if time_diff < 24.0:
                    ui.notify(
                        f"Warning (Step {idx}): Scheduled time must be at least 24 hours after the previous step!",
                        type='warning',
                        duration=6000
                    )
            if current_dt:
                last_scheduled_dt = current_dt
        else:
            act_rcm = "TBD"
            act_date = "TBD"

        base_name_raw = get_val(row['name'], row['name_other'])
        ndmp_cnt = row['ndmp_count'].value
        add_acts_list = row['add_acts'].value if isinstance(row['add_acts'].value, list) else []
        manual_duration = row['duration'].value
        multi_step_flag = row['multi_step'].value

        act_name = compute_combined_activity_name(base_name_raw, ndmp_cnt, add_acts_list)
        
        raw_hrs, cust_buffered_hrs, internal_planned_hrs = calculate_activity_duration(
            model_val, base_name_raw, ndmp_cnt, add_acts_list, manual_duration
        )

        internal_act_lines.append(
            f"{act_rcm} | {act_name} | {act_from} → {act_to} | {act_date} | Base Duration: {raw_hrs}h | Planned Duration: {internal_planned_hrs}h (Internal Buffer +1h) | Status: {sched_status} | Multi-Step: {multi_step_flag}"
        )

        customer_act_sections.append(
            f"Step {idx}: {act_name}\n"
            f"  • RCM Activity ID   : {act_rcm}\n"
            f"  • Schedule Status   : {sched_status}\n"
            f"  • Version Transition: {act_from} → {act_to}\n"
            f"  • Scheduled Date    : {act_date}\n"
            f"  • Duration          : {cust_buffered_hrs} Hours\n"
            f"  • NDMP Count        : {ndmp_cnt}\n"
            f"  • Additional Acts   : {', '.join(add_acts_list)}"
        )

        if act_to != 'NA':
            oe_pkg = next((p for p in PACKAGE_DATABASE if p["type"] == "IDPA OE" and p["version"] == act_to), None)
            if oe_pkg: required_packages.append(oe_pkg)

            if ndmp_cnt != 'No':
                ndmp_pkg = next((p for p in PACKAGE_DATABASE if p["type"] == "NDMP" and p["applicableFor"] == f"NDMP for {act_to}"), None)
                if ndmp_pkg: required_packages.append(ndmp_pkg)

            if 'AVE /space expansion' in add_acts_list and act_to == "2.7.2":
                ave_pkg = next((p for p in PACKAGE_DATABASE if p["type"] == "AVE /space"), None)
                if ave_pkg: required_packages.append(ave_pkg)

            if 'DDOS Upgrade' in add_acts_list or act_to == 'DDOS Upgrade':
                ddos_pkg = next((p for p in PACKAGE_DATABASE if p["type"] == "DDOS"), None)
                if ddos_pkg: required_packages.append(ddos_pkg)

            if 'Hotfix Upgrade' in add_acts_list or act_to == 'Hotfix Upgrade':
                hf_pkg = next((p for p in PACKAGE_DATABASE if p["type"] == "Hotfix" and p["applicableFor"] == act_to), None)
                if hf_pkg: required_packages.append(hf_pkg)

    seen_ids = set()
    unique_packages = []
    for pkg in required_packages:
        if pkg["id"] not in seen_ids:
            seen_ids.add(pkg["id"])
            unique_packages.append(pkg)

    acm_val_str = f"{get_val(acm_dashboard, acm_details)}" + (f" (Details: {acm_details.value})" if acm_details.value and 'Issues' in acm_dashboard.value else "")
    ruck_val_str = f"{get_val(ruck_status, ruck_details)}" + (f" (Details: {ruck_details.value})" if ruck_details.value and 'Issues' in ruck_status.value else "")
    
    health_val_str = f"{get_val(health_status, health_issue_details)}" + (f" (Details: {health_issue_details.value})" if health_issue_details.value and ('not healthy' in health_status.value or health_status.value == 'Other') else "")

    sr_template = f"""*** POWERPROTECT DP TECHNICAL CONSULTATION (TC) SUMMARY ***

1. CUSTOMER & SYSTEM DETAILS
Customer Name: {cust_name.value}
Customer Site / Location: {cust_loc.value}
Upgrade SR: {sr_num.value}
PowerProtect DP Serial Number: {serial_num.value}
IDPA Model: {model_val}
Current Code: {curr_val}
Code Requested: {req_val}
Code Recommended: {rec_val}
Code Confirmed: {conf_val}
Upgrade Request Notes: {upg_notes.value}

2. SYSTEM HEALTH & PREPARATION
ACM Dashboard Status: {acm_val_str}
PDF Status: {get_val(pdf_status, pdf_other)}
RUCK Status: {ruck_val_str}
ACM VM Snapshot: {get_val(acm_snapshot, acm_snap_other)}
Validation Status: {get_val(validation_status, val_stat_other)}
iDRAC Status: {get_val(idrac_status, idrac_other)}
Exceptional Tasks: {get_val(exceptional_tasks, exc_other)}
Upgrade Health Status: {health_val_str}

3. UPGRADE PREPARATION STATUS
UPG Review: {get_val(upg_review, upg_rev_other)}
Prerequisites: {get_val(prereqs_status, prereq_other)}
Code Stage: {get_val(download_status, dl_stat_other)}

4. UPGRADE PATH & SCHEDULE
Upgrade Path: {upgrade_path_str}

RCM SCHEDULE & ACTIVITIES:
""" + "\n".join(internal_act_lines) + f"""

5. SCHEDULING ACTION
Action Taken: {get_val(scheduling_action, sched_act_other)}"""

    if unique_packages:
        col_type = max(len(p['type']) for p in unique_packages)
        col_type = max(col_type, 12)
        col_ver = max(len(p['version']) for p in unique_packages)
        col_ver = max(col_ver, 7)
        col_file = max(len(p['filename']) for p in unique_packages)
        col_file = max(col_file, 35)
        col_size = max(len(p['size']) for p in unique_packages)
        col_size = max(col_size, 6)

        table_header = f"+-{'-'*col_type}-+-{'-'*col_ver}-+-{'-'*col_file}-+-{'-'*col_size}-+-{'='*15}-+"
        table_title  = f"| {'Package Type'.ljust(col_type)} | {'Version'.ljust(col_ver)} | {'Filename'.ljust(col_file)} | {'Size'.ljust(col_size)} | {'Download Link'.ljust(15)} |"
        
        table_rows = []
        for p in unique_packages:
            table_rows.append(
                f"| {p['type'].ljust(col_type)} | {p['version'].ljust(col_ver)} | {p['filename'].ljust(col_file)} | {p['size'].ljust(col_size)} | {p['download'].ljust(15)} |"
            )
        
        package_table_formatted = "\n".join([table_header, table_title, table_header] + table_rows + [table_header])
    else:
        package_table_formatted = "No specific packages staged."

    docs_formatted = "\n".join([f"• {d['name']}: {d['url']}" for d in REF_DOCUMENTS])
    steps_formatted = "\n\n".join(customer_act_sections)

    customer_email_body = f"""#TechConsult

Hello {cust_name.value or 'Customer'},

I have completed the technical consultation and pre-checks for your PowerProtect DP upgrade.

================================================================================
CUSTOMER ACTION SUMMARY
================================================================================

Required:
  • Download required upgrade package(s).
  • Upload packages to the PowerProtect DP system.
  • Verify package checksum.
  • Review Release Notes and complete prerequisites.
  • Resolve upgrade-blocking issues.
  • Disable backup policies before the applicable upgrade activity.

Recommended:
  • Review the Upgrade Preparation Guide.
  • Verify compatibility and upgrade requirements.
  • Ensure business continuity.

================================================================================
TECHNICAL CONSULTATION DETAILS
================================================================================
Customer Name              : {cust_name.value}
Customer Site / Location   : {cust_loc.value}
Upgrade SR                 : {sr_num.value}
PowerProtect DP Serial No. : {serial_num.value}
IDPA Model                 : {model_val}
Current Code               : {curr_val}
Code Confirmed             : {conf_val}

OVERALL HEALTH STATUS
  • {get_val(health_status, health_issue_details)}

UPGRADE PATH
  • {upgrade_path_str}

================================================================================
UPGRADE SCHEDULE & STEPS
================================================================================
{steps_formatted}

================================================================================
UPGRADE PACKAGES
================================================================================
{package_table_formatted}

================================================================================
REFERENCE DOCUMENTS
================================================================================
{docs_formatted}

================================================================================
RESPONSIBILITIES
================================================================================
Dell / Support Responsibilities:
  • Review system health and validate the upgrade path.
  • Perform applicable pre-checks.
  • Execute the upgrade according to the agreed plan.
  • Perform post-upgrade validation.

Customer Responsibilities:
  • Download and stage required software.
  • Verify package checksums.
  • Review the Upgrade Preparation Guide and Release Notes.
  • Complete prerequisites and compatibility checks.
  • Disable backup policies before the applicable activity.
  • Complete required client/proxy/plugin updates after the upgrade.
  • Resolve upgrade-blocking issues before the applicable activity.

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

def download_eml_file(subject, body, filename):
    if not body:
        ui.notify('Please generate deliverables first!', type='warning')
        return
    
    eml_content = (
        f"Subject: {subject}\n"
        f"From: support@dell.com\n"
        f"To: \n"
        f"MIME-Version: 1.0\n"
        f"Content-Type: text/plain; charset=utf-8\n\n"
        f"{body}"
    )
    ui.download(eml_content.encode('utf-8'), filename)
    ui.notify(f'Downloading Outlook Email file ({filename})... Open it in Outlook to add recipient and send!', type='positive')

# --- ENVIRONMENT PORT BINDING FOR RENDER / LOCAL ---
port = int(os.environ.get("PORT", 8080))

ui.run(
    title="Technical Consultation Portal",
    host="0.0.0.0",
    port=port,
    reload=False
)