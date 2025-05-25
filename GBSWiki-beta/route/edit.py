from .tool.func import *
from custom_route.tools import *


def edit(name = 'Test', name_load = 0, section = 0):
    with get_db_connect() as conn:
        curs = conn.cursor()
    
        ip = ip_check()
        if acl_check(name) == 1:
            return re_error('/ban')

        if name == '' or name == '%20':
            return custom_re_error('/no_input')

        curs.execute(db_change("select id from history where title = ? order by id + 0 desc"), [name])
        doc_ver = curs.fetchall()
        doc_ver = doc_ver[0][0] if doc_ver else '0'
        
        section = '' if section == 0 else section
        post_ver = flask.request.form.get('ver', '')
        if flask.request.method == 'POST':
            edit_repeat = 'error' if post_ver != doc_ver else 'post'
        else:
            edit_repeat = 'get'
        
        if edit_repeat == 'post':
            if captcha_post(flask.request.form.get('g-recaptcha-response', flask.request.form.get('g-recaptcha', ''))) == 1:
                return re_error('/error/13')
            else:
                captcha_post('', 0)
    
            if slow_edit_check() == 1:
                return re_error('/error/24')
    
            today = get_time()
            content = flask.request.form.get('content', '').replace('\r\n', '\n')

            if content == '':
                return custom_re_error('/no_input')

            if doc_ver != '0':
                curs.execute(db_change("select data from data where title = ?"), [name])
                content_present = (curs.fetchall())[0][0]
                if len(content_present) == len(content):
                    if content_present == content:
                        if (flask.request.form.get('close', '') and check_close(conn, name)) or (not flask.request.form.get('close', '') and not check_close(conn, name)):
                            return custom_re_error('/not_changed')
            
            if edit_filter_do(content) == 1:
                return re_error('/error/21')
                
            curs.execute(db_change('select data from other where name = "copyright_checkbox_text"'))
            copyright_checkbox_text_d = curs.fetchall()
            if copyright_checkbox_text_d and copyright_checkbox_text_d[0][0] != '' and flask.request.form.get('copyright_agreement', '') != 'yes':
                return re_error('/error/29')
            
            curs.execute(db_change("select data from data where title = ?"), [name])
            old = curs.fetchall()
            if old:  
                o_data = old[0][0].replace('\r\n', '\n')
    
                leng = leng_check(len(o_data), len(content))
                
                curs.execute(db_change("update data set data = ? where title = ?"), [content, name])
            else:
                leng = '+' + str(len(content))
    
                curs.execute(db_change("insert into data (title, data) values (?, ?)"), [name, content])
    
                curs.execute(db_change('select data from other where name = "count_all_title"'))
                curs.execute(db_change("update other set data = ? where name = 'count_all_title'"), [str(int(curs.fetchall()[0][0]) + 1)])
    
            curs.execute(db_change("select user from scan where title = ? and type = ''"), [name])
            for scan_user in curs.fetchall():
                add_alarm(scan_user[0], ip + ' | <a href="/w/' + url_pas(name) + '">' + name + '</a> | Edit')
                    
            history_plus(
                name,
                content,
                today,
                ip,
                flask.request.form.get('send', ''),
                leng
            )
            
            curs.execute(db_change("delete from back where link = ?"), [name])
            curs.execute(db_change("delete from back where title = ? and type = 'no'"), [name])
            if flask.request.form.get('close', ''):
                set_close(conn, name, 1)
            else: set_close(conn, name, 0)

            render_set(
                doc_name = name,
                doc_data = content,
                data_type = 'backlink'
            )
            
            conn.commit()
            
            section = (('#edit_load_' + str(section)) if section != '' else '')
            
            return redirect('/w/' + url_pas(name) + section)
        else:
            editor_top_text = ''
            if edit_repeat == 'get':
                load_title = name_load
                print(load_title, section)
                if load_title == 0 and section == '':
                    load_title = name
                    editor_top_text += '<a href="/manager/15/' + url_pas(name) + '">(' + load_lang('load') + ')</a> '
                elif section != '':
                    load_title = name
                    
                curs.execute(db_change("select data from data where title = ?"), [load_title])
                sql_d = curs.fetchall()
                data = sql_d[0][0] if sql_d else ''
                data = data.replace('\r\n', '\n')
            else:
                data = flask.request.form.get('content', '')
                warning_edit = load_lang('exp_edit_conflict') + ' '
    
                if flask.request.form.get('ver', '0') == '0':
                    warning_edit += '<a href="/raw/' + url_pas(name) + '">(r' + doc_ver + ')</a>'
                else:
                    warning_edit += '' + \
                        '<a href="/diff/' + flask.request.form.get('ver', '1') + '/' + doc_ver + '/' + url_pas(name) + '">' + \
                            '(r' + doc_ver + ')' + \
                        '</a>' + \
                    ''
    
                warning_edit += '<hr class="main_hr">'
                editor_top_text = warning_edit + editor_top_text
    
            editor_top_text += '' + \
                '<a href="/edit_filter">(' + load_lang('edit_filter_rule') + ')</a>' + \
                '<hr class="main_hr">' + \
            ''
    
            curs.execute(db_change('select data from other where name = "edit_bottom_text"'))
            sql_d = curs.fetchall()
            b_text = ('<hr class="main_hr">' + sql_d[0][0]) if sql_d and sql_d[0][0] != '' else ''
            
            curs.execute(db_change('select data from other where name = "copyright_checkbox_text"'))
            sql_d = curs.fetchall()
            if sql_d and sql_d[0][0] != '':
                cccb_text = '' + \
                    '<hr class="main_hr">' + \
                    '<input type="checkbox" name="copyright_agreement" value="yes"> ' + sql_d[0][0] + \
                    '<hr class="main_hr">' + \
                ''
            else:
                cccb_text = ''
    
            curs.execute(db_change('select data from other where name = "edit_help"'))
            sql_d = curs.fetchall()
            p_text = html.escape(sql_d[0][0]) if sql_d and sql_d[0][0] != '' else load_lang('default_edit_help')
    
            data = re.sub(r'\n+$', '', data)
    
            monaco_on = flask.request.cookies.get('main_css_monaco', '0')
            if monaco_on == '1':
                editor_display = 'style="display: none;"'
                monaco_display = ''
                add_get_file = '''
                    <link   rel="stylesheet"
                            data-name="vs/editor/editor.main" 
                            href="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.20.0/min/vs/editor/editor.main.min.css">
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.20.0/min/vs/loader.min.js"></script>
                '''
                
                if flask.request.cookies.get('main_css_darkmode', '0') == '1':
                    monaco_thema = 'vs-dark'
                else:
                    monaco_thema = ''
                
                add_script = '''
                    require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.20.0/min/vs' }});
                    require(["vs/editor/editor.main"], function () {
                        window.editor = monaco.editor.create(document.getElementById('monaco_editor'), {
                            value: document.getElementById('textarea_edit_view').value,
                            language: 'plaintext',
                            theme: \'''' + monaco_thema + '''\'
                        });
                    });
                '''
            else:
                editor_display = ''
                monaco_display = 'style="display: none;"'
                add_get_file = ''
                add_script = ''
                
            curs.execute(db_change("select data from other where name = 'markup'"))
            markup = curs.fetchall()[0][0]
            
            server_set = {
                'section' : section,
                'markup' : markup
             }

            if check_close(conn, name):
                close = 'checked'
            else: close = ''

            return easy_minify(flask.render_template(skin_check(), 
                imp = [name, wiki_set(), wiki_custom(), wiki_css(['(' + load_lang('edit') + ')', 0])],
                data =  editor_top_text + add_get_file + '''
                    <span   id="server_set"
                            style="display: none;">''' + json.dumps(server_set) + '''</span>
                    <form method="post">
                        <div>''' + edit_button(monaco_on) + '''</div>
                        <div    id="monaco_editor"
                                class="content" 
                                ''' + monaco_display + '''></div>
                        <textarea   id="textarea_edit_view"
                                    ''' + editor_display + '''
                                    class="content"
                                    placeholder="''' + p_text + '''">''' + html.escape(data) + '''</textarea>
                        <hr class="main_hr">
                        <input  placeholder="''' + load_lang('why') + '''" 
                                name="send">
                        <hr class="main_hr">
                        <textarea   style="display: none;" 
                                    id="origin">''' + html.escape(data) + '''</textarea>
                        <textarea   style="display: none;"
                                    name="content"
                                    id="content"></textarea>
                        <input  style="display: none;" 
                                name="ver" 
                                value="''' + doc_ver + '''">
                        <hr class="main_hr">
                        ''' + captcha_get() + ip_warning() + cccb_text + '''
                        <button id="save"
                                type="submit" 
                                onclick="
                                    monaco_to_content(); 
                                    save_stop_exit();
                                    section_edit_do();
                                ">''' + load_lang('save') + '''</button>
                        <button id="preview" 
                                type="button" 
                                onclick="
                                    monaco_to_content();
                                    load_preview(\'''' + url_pas(name) + '''\');
                                ">''' + load_lang('preview') + '''</button>
                    </form>
                    ''' + b_text + '''
                    <hr class="main_hr">
                    <div id="see_preview"></div>
                    <script>
                        section_edit_init();
                        do_paste_image();
                        do_not_out();
                        ''' + add_script + '''
                    </script>
                ''',
                menu = [
                    ['w/' + url_pas(name), load_lang('return')],
                    ['delete/' + url_pas(name), load_lang('delete')], 
                    ['move/' + url_pas(name), load_lang('move')], 
                    ['upload', load_lang('upload')]
                ]
            ))