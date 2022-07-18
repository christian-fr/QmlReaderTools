from pathlib import Path

path_here = Path(__file__).parent

input_qml_01_test_file = Path(path_here, 'qml', 'questionnaire_01.xml')

questionnaire_variables_str = "['width: number', 'height: number', 'isMobile: boolean', 'jsCheck: boolean', 'url: string', 'flag_index: boolean', 'var01: boolean', 'var02: singleChoiceAnswerOption', 'flag_A01: boolean', 'var03a: string', 'var03b: string', 'var03c: string', 'var03d: string', 'var03e: string', 'var03f: string', 'var03g: string', 'var03h: string', 'var03i: string', 'var03j: string', 'var03k: string', 'var04: string', 'var05: singleChoiceAnswerOption', 'var06: string']"
questionnaire_digraph_edges_str = r"[('index\n\n[var01, url, jsCheck,\nisMobile]', 'A01\n\n[var02, flag_A01]'), ('index\n\n[var01, url, jsCheck,\nisMobile]', 'A02\n\n[var03a, var03b, var03c,\nvar03d, var03e, var03f,\nvar03g, var03h, var03i,\nvar03j, var03k]'), ('index\n\n[var01, url, jsCheck,\nisMobile]', 'A03\n\n[var04]'), ('A01\n\n[var02, flag_A01]', 'A03\n\n[var04]'), ('A02\n\n[var03a, var03b, var03c,\nvar03d, var03e, var03f,\nvar03g, var03h, var03i,\nvar03j, var03k]', 'A04\n\n[var05]'), ('A03\n\n[var04]', 'A05\n\n[var06]'), ('A04\n\n[var05]', 'A06\n\n[var07]'), ('A05\n\n[var06]', 'A06\n\n[var07]'), ('A06\n\n[var07]', 'end')]"
questionnaire_pages_list = ['index', 'A01', 'A02', 'A03', 'A04', 'A05', 'A06', 'end']


