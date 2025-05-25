from .func_tool import *

# 커스텀 마크 언젠간 다시 추가 예정

class class_do_render:
    def __init__(self, conn):
        self.conn = conn
    
    def do_backlink_generate(self, data_markup, doc_data, doc_name):
        conn = self.conn
        curs = self.conn.cursor()

        if data_markup == 'namumark':
            # Link
            link_re = re.compile(r'\[\[(?!https?:\/\/|inter:|외부:|out:|#)((?:(?!\[\[|\]\]|\|).)+)(?:\]\]|\|)', re.I)

            data_link = link_re.findall(doc_data)
            data_link = list(set(data_link))

            data_link_end = {}
            data_link_end['cat'] = []
            data_link_end['file'] = []
            data_link_end['link'] = []

            data_link_end_all = []

            for i in data_link:
                data_link_in = i
                if  data_link_in.startswith('분류:') or \
                    data_link_in.startswith('category:'):
                    data_link_in = re.sub(r'\\(.)', r'\1', data_link_in)
                    data_link_end['cat'] += [re.sub(r'^분류:', 'category:', data_link_in)]
                elif data_link_in.startswith('파일:') or \
                    data_link_in.startswith('file:'):
                    data_link_in = re.sub(r'\\(.)', r'\1', data_link_in)
                    data_link_end['file'] += [re.sub(r'^파일:', 'file:', data_link_in)]
                else:
                    data_link_in = re.sub(r'([^\\])#(?:[^#]*)$', r'\1', data_link_in)

                    if data_link_in[0] == ':':
                        data_link_in = re.sub(r'^:분류:', 'category:', data_link_in)
                        data_link_in = re.sub(r'^:category:', 'category:', data_link_in)

                        data_link_in = re.sub(r'^:file:', 'file:', data_link_in)
                        data_link_in = re.sub(r'^:파일:', 'file:', data_link_in)
                    elif data_link_in[0] == '/':
                        data_link_in = doc_name + data_link_in
                    elif len(data_link_in) >= 3 and data_link_in[0:3] == '../':
                        data_link_in = data_link_in[3:len(data_link_in)]
                        data_link_in = '' + \
                            re.sub('\/[^/]+$', '', doc_name) + \
                            (('/' + data_link_in) if data_link_in != '' else '') + \
                        ''

                    data_link_in = re.sub(r'\\(.)', r'\1', data_link_in)
                    data_link_end['link'] += [data_link_in]

            if data_link_end != {}:
                data_link_end['cat'] = list(set(data_link_end['cat']))
                data_link_end['file'] = list(set(data_link_end['file']))
                data_link_end['link'] = list(set(data_link_end['link']))

                data_link_end_all += [[doc_name, i, 'cat'] for i in data_link_end['cat']]
                data_link_end_all += [[doc_name, i, 'file'] for i in data_link_end['file']]
                data_link_end_all += [[doc_name, i, ''] for i in data_link_end['link']]

                data_link_no = []
                for i in data_link_end['link']:
                    curs.execute(db_change("select title from data where title = ?"), [i])
                    if not curs.fetchall():
                        data_link_no += [[doc_name, i, 'no']]

                data_link_end_all += data_link_no

            # Include
            include_re = re.compile(r'\[include\(((?:(?!\)\]).)+)\)\]', re.I)

            data_include = include_re.findall(doc_data)
            data_include = list(set(data_include))

            for i in data_include:
                data_include_in = i
                data_include_in = re.sub(r'([^\\]),.*$', r'\1', data_include_in)

                data_link_end_all += [[doc_name, data_include_in, 'include']]

            # Redirect
            redirect_re = re.compile(r'^#(?:redirect|넘겨주기) ([^\n]+)', re.I)

            data_redirect = redirect_re.search(doc_data)
            if data_redirect:
                data_redirect = data_redirect.group(1)

                data_redirect = re.sub(r'([^\\])#(?:[^#]*)$', r'\1', data_redirect)

                data_link_end_all += [[doc_name, data_redirect, 'redirect']]
        else:
            # markup == null
            data_link_end_all = []

        return data_link_end_all

    def do_render(self, doc_name, doc_data, data_type, data_in):
        conn = self.conn
        curs = self.conn.cursor()

        data_in = None if data_in == '' else data_in

        curs.execute(db_change('select data from other where name = "markup"'))
        rep_data = curs.fetchall()
        rep_data = rep_data[0][0] if rep_data else 'namumark'

        if data_type != 'backlink':
            if rep_data == 'namumark':
                data_in = (data_in + '_') if data_in else ''
                data_end = [
                    '<pre style="display: none;" id="' + data_in + 'render_content_load">' + html.escape(doc_data) + '</pre>' + \
                    '<div class="render_content" id="' + data_in + 'render_content"></div>', 
                    '''
                        do_onmark_render(
                            test_mode = "normal", 
                            name_id = "''' + data_in + '''render_content",
                            name_include = "''' + data_in + '''",
                            name_doc = "''' + html.escape(doc_name.replace('"', '\\"')) + '''"
                        );
                    ''',
                    []
                ]
            elif rep_data == 'markdown':
                data_in = (data_in + '_') if data_in else ''
                data_end = [
                    '<pre style="display: none;" id="' + data_in + 'render_content_load">' + html.escape(doc_data) + '</pre>' + \
                    '<div class="render_content" id="' + data_in + 'render_content"></div>', 
                    '''
                        do_onmark_render(
                            test_mode = "normal", 
                            name_id = "''' + data_in + '''render_content",
                            name_include = "''' + data_in + '''",
                            name_doc = "''' + html.escape(doc_name.replace('"', '\\"')) + '''"
                        );
                    ''',
                    []
                ]
            else:
                data_end = [
                    doc_data, 
                    '', 
                    []
                ]

            if data_type == 'api_view':
                return [
                    data_end[0], 
                    data_end[1]
                ]
            else:
                return data_end[0] + '<script>' + data_end[1] + '</script>'
        else:
            backlink = self.do_backlink_generate(
                rep_data, 
                doc_data, 
                doc_name
            )

            if backlink != []:
                curs.executemany(db_change("insert into back (link, title, type) values (?, ?, ?)"), backlink)
                curs.execute(db_change("delete from back where title = ? and type = 'no'"), [doc_name])

            conn.commit()