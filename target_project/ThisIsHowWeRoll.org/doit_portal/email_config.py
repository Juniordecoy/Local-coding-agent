# email_config.py

EMAILS = {
    "CL": "claganke@doitoutdoors.com",
    "LS": "lsimon@doitoutdoors.com",
    "RH": "rharper@doitoutdoors.com",
    "JB": "jbeck@doitoutdoors.com",
    "ER": "erodriguez@doitoutdoors.com",
    "CW": "cwilkins@doitoutdoors.com",

    "SJ": "sjewell@doitoutdoors.com",
    "KL": "klaird@doitoutdoors.com",

    "MH1": "xerox561@aol.com",
    "MH2": "markhooper0511@icloud.com",
    "RS": "rsantiago@doitoutdoors.com",

    "CB": "cassandrabell32@gmail.com",
    "JLB": "jbusiness1@yahoo.com",
    "RL": "robbielezama975@gmail.com",
    "MM": "mike71023@yahoo.com",
    "GR": "garyrausin@gmail.com",
    "CV": "carloselcopa@gmail.com",

    "CAREERS": "careers@doitoutdoors.com",
    "POSTING": "posting@doitoutdoors.com",
    "PAPERWORK": "paperwork@doitoutdoors.com",
}

FORM_EMAIL_MAP1 = {
    "lead_shop":                [EMAILS["ER"]],
    "lead_applicant_feedback":  [EMAILS["ER"]],
    "contactreport":            [EMAILS["ER"]],
    "postingphotos":            [EMAILS["ER"]],
    "photo_quiz":               [EMAILS["ER"]],
    "dan_kelly_voting":         [EMAILS["ER"]],
    "harassment_training":      [EMAILS["ER"]],
    "dot_compliance_test":      [EMAILS["ER"]],
    "acknowledgement_form":     [EMAILS["ER"]],
    "samsara_notice":           [EMAILS["ER"]],
    "near_miss_reporting":      [EMAILS["ER"]],
    "monthly_quiz":             [EMAILS["ER"]],
    "week_test":                [EMAILS["ER"]],
    "ojt_checklist":            [EMAILS["ER"]],
    "post_training_recap":      [EMAILS["ER"]],
    "return_to_work_quiz":      [EMAILS["ER"]],
    "driver_questions":         [EMAILS["ER"]],
    "driver_feedback":          [EMAILS["ER"]],
    "upcoming_campaign":        [EMAILS["ER"]],
    "ucr":                      [EMAILS["ER"]],
    "driver_intro":             [EMAILS["ER"]],
    "vehicle_accident_report":  [EMAILS["ER"]],
    "planning_practice_assignment":  [EMAILS["ER"]],
}

FORM_EMAIL_MAP = {
    "lead_shop":                [EMAILS["LS"]],
    "lead_applicant_feedback":  [EMAILS["ER"]],
    "contactreport":            [EMAILS["CL"], EMAILS["LS"], EMAILS["JB"], EMAILS["RS"], EMAILS["MH1"]],
    "postingphotos":            [EMAILS["LS"], EMAILS["POSTING"]],
    "photo_quiz":               [EMAILS["CW"]],
    "dan_kelly_voting":         [EMAILS["LS"]],
    "harassment_training":      [EMAILS["ER"]],
    "dot_compliance_test":      [EMAILS["CL"], EMAILS["LS"], EMAILS["JB"], EMAILS["SJ"], EMAILS["KL"]],
    "acknowledgement_form":     [EMAILS["RH"]],
    "samsara_notice":           [EMAILS["JB"]],
    "near_miss_reporting":      [EMAILS["CL"], EMAILS["LS"], EMAILS["JB"]],
    "monthly_quiz":             [EMAILS["JB"], EMAILS["ER"]],
    "week_test":                [EMAILS["SJ"], EMAILS["KL"], EMAILS["CV"], EMAILS["GR"], EMAILS["MM"],
                                 EMAILS["RL"], EMAILS["JLB"], EMAILS["CB"], EMAILS["RS"], EMAILS["MH1"]],
    "ojt_checklist":            [EMAILS["SJ"], EMAILS["KL"]],
    "post_training_recap":      [EMAILS["CL"], EMAILS["LS"], EMAILS["JB"], EMAILS["SJ"], EMAILS["KL"]],
    "return_to_work_quiz":      [EMAILS["CL"], EMAILS["LS"], EMAILS["JB"]],
    "driver_questions":         [EMAILS["ER"]],
    "driver_feedback":          [EMAILS["PAPERWORK"]],
    "upcoming_campaign":        [EMAILS["LS"], EMAILS["RH"]],
    "ucr":                      [EMAILS["PAPERWORK"], EMAILS["CV"], EMAILS["GR"], EMAILS["MM"], EMAILS["RL"],
                                 EMAILS["JLB"], EMAILS["CB"], EMAILS["RS"], EMAILS["MH2"]],
    "vehicle_accident_report":  [EMAILS["ER"], EMAILS["CL"], EMAILS["JB"],  EMAILS["RS"], EMAILS["MH1"]],
    "driver_intro":             [EMAILS["CAREERS"]],
    "planning_practice_assignment":  [EMAILS["CAREERS"]],
}


# Emails & Names that are NOT allowed to submit forms
BLOCKED_EMAILS = {
    "coulombe.floyd@outlook.com",
    "zekisuquc419@gmail.com",
    "hil.eripo435@gmail.com",
    "ericjonesmyemail@gmail.com",
    "zubia.lyn@outlook.com",
    "yyoiyokf@immenseignite.info",
    "udes.a.p.o.faz.i41.2@gmail.com",
    "denis.krasnikovvlb@gmail.com",
}

BLOCKED_NAMES = [
    "jaym smith",
    "Baires_Vibesacala",
    "Cultura_SeguraPEP",
]