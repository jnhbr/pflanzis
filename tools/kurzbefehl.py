import plistlib, uuid, re, os, sys

code, out = sys.argv[1], sys.argv[2]
cfg = open(os.path.expanduser('~/Desktop/Claude/Projekte/pflanzis/config.js')).read()
key = re.search(r'AIza[A-Za-z0-9_-]+', cfg).group(0)
URL = f'https://firestore.googleapis.com/v1/projects/meine-r/databases/(default)/documents/pflanzis/{code}/export/erinnerungen?key={key}'

U = lambda: str(uuid.uuid4()).upper()
def ref(u, name): return {'OutputUUID': u, 'Type': 'ActionOutput', 'OutputName': name}
def att(u, name): return {'Value': ref(u, name), 'WFSerializationType': 'WFTextTokenAttachment'}
def tok(u, name): return {'Value': {'string': '￼', 'attachmentsByRange': {'{0, 1}': ref(u, name)}}, 'WFSerializationType': 'WFTextTokenString'}
def txt(s): return {'Value': {'string': s, 'attachmentsByRange': {}}, 'WFSerializationType': 'WFTextTokenString'}
def var(n): return {'Value': {'Type': 'Variable', 'VariableName': n}, 'WFSerializationType': 'WFTextTokenAttachment'}
def vartok(n): return {'Value': {'string': '￼', 'attachmentsByRange': {'{0, 1}': {'Type': 'Variable', 'VariableName': n}}}, 'WFSerializationType': 'WFTextTokenString'}
def act(ident, **p): return {'WFWorkflowActionIdentifier': ident, 'WFWorkflowActionParameters': p}
def ende(g): return act('is.workflow.actions.conditional', GroupingIdentifier=g, WFControlFlowMode=2, UUID=U())
DV = 'Dictionary Value'

u_text, u_dl, u_val, u_dict, u_find, u_vorh, u_date = (U() for _ in range(7))
A = [
    act('is.workflow.actions.gettext', UUID=u_text, WFTextActionText=txt(URL)),
    act('is.workflow.actions.downloadurl', UUID=u_dl, WFURL=tok(u_text, 'Text')),
    act('is.workflow.actions.getvalueforkey', UUID=u_val, WFInput=att(u_dl, 'Contents of URL'),
        WFGetDictionaryValueType='Value', WFDictionaryKey=txt('fields.json.stringValue')),
    act('is.workflow.actions.detect.dictionary', UUID=u_dict, CustomOutputName='Plan', WFInput=att(u_val, DV)),
    # alle Erinnerungen nur LESEN (für die Doppelt-Prüfung)
    act('is.workflow.actions.filter.reminders', UUID=u_find),
    act('is.workflow.actions.gettext', UUID=u_vorh, CustomOutputName='Vorhanden', WFTextActionText=tok(u_find, 'Reminders')),
    act('is.workflow.actions.date', UUID=u_date, WFDateActionMode='Current Date'),
]

# 7 Tage ausgeschrieben (feste Zahlen, kein Repeat Index): neue Tage in Variable «Neu» sammeln
for d in range(7):
    ua, uf, ut, ui = U(), U(), U(), U()
    g1, g2 = U(), U()
    A += [
        act('is.workflow.actions.adjustdate', UUID=ua, WFDate=tok(u_date, 'Date'), WFAdjustOperation='Add',
            WFDuration={'Value': {'Magnitude': d, 'Unit': 'days'}, 'WFSerializationType': 'WFQuantityFieldValue'}),
        act('is.workflow.actions.format.date', UUID=uf, WFDateFormatStyle='Custom', WFDateFormat='yyyy-MM-dd',
            WFDate=tok(ua, 'Adjusted Date')),
        act('is.workflow.actions.getvalueforkey', UUID=ut, CustomOutputName=f'Tag {d}', WFInput=att(u_dict, 'Dictionary'),
            WFGetDictionaryValueType='Value', WFDictionaryKey=tok(uf, 'Formatted Date')),
        act('is.workflow.actions.conditional', GroupingIdentifier=g1, WFControlFlowMode=0, WFCondition=100,
            WFInput={'Type': 'Variable', 'Variable': att(ut, DV)}),
        act('is.workflow.actions.getvalueforkey', UUID=ui, CustomOutputName=f'titel {d}', WFInput=att(ut, DV),
            WFGetDictionaryValueType='Value', WFDictionaryKey=txt('titel')),
        act('is.workflow.actions.conditional', GroupingIdentifier=g2, WFControlFlowMode=0, WFCondition=999,
            WFInput={'Type': 'Variable', 'Variable': att(u_vorh, 'Text')}, WFConditionalActionString=tok(ui, DV)),
        act('is.workflow.actions.getvalueforkey', UUID=(z:=U()), CustomOutputName=f'zeit {d}', WFInput=att(ut, DV),
            WFGetDictionaryValueType='Value', WFDictionaryKey=txt('zeit')),
        act('is.workflow.actions.getvalueforkey', UUID=(n:=U()), CustomOutputName=f'notiz {d}', WFInput=att(ut, DV),
            WFGetDictionaryValueType='Value', WFDictionaryKey=txt('notiz')),
        act('is.workflow.actions.addnewreminder', UUID=U(), WFCalendarItemTitle=tok(ui, DV), WFCalendarItemCalendar=txt('Pflanzis'),
            WFAlertEnabled='Alert', WFAlertCondition='At Time', WFAlertCustomTime=tok(z, DV), WFCalendarItemNotes=tok(n, DV)),
        ende(g2),
        ende(g1),
    ]

assert not any('remove' in a['WFWorkflowActionIdentifier'] for a in A)

wf = {
    'WFWorkflowActions': A,
    'WFWorkflowClientVersion': '2605.0.5',
    'WFWorkflowMinimumClientVersion': 900,
    'WFWorkflowMinimumClientVersionString': '900',
    'WFWorkflowIcon': {'WFWorkflowIconStartColor': 4292093695, 'WFWorkflowIconGlyphNumber': 59511},
    'WFWorkflowImportQuestions': [{'ActionIndex': i, 'Category': 'Parameter', 'DefaultValue': 'Pflanzis', 'ParameterKey': 'WFCalendarItemCalendar',
        'Text': f'Liste für Tag {k+1} von 7: bitte «Pflanzis» wählen'} for k,i in enumerate(i for i,a in enumerate(A) if a['WFWorkflowActionIdentifier'].endswith('addnewreminder'))],
    'WFWorkflowInputContentItemClasses': [],
    'WFWorkflowOutputContentItemClasses': [],
    'WFWorkflowTypes': [],
    'WFWorkflowHasShortcutInputVariables': False,
    'WFQuickActionSurfaces': [],
}
with open(out, 'wb') as f:
    plistlib.dump(wf, f, fmt=plistlib.FMT_BINARY)
print('ok', len(A), 'Aktionen')
