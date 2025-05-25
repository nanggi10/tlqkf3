from .tool.func import *

def list_admin_use_2(conn):
    curs = conn.cursor()

    num = int(number_check(flask.request.args.get('num', '1')))
    sql_num = (num * 50 - 50) if num * 50 > 0 else 0

    if flask.request.method == 'POST':
        return redirect('/admin_log?search=' + flask.request.form.get('search', 'normal'))
    else:
        list_data = '<ul class="inside_ul">'

        if flask.request.args.get('search', 'normal') == 'normal':
            curs.execute(db_change("select who, what, time from re_admin order by time desc limit ?, 50"), [sql_num])
        else:
            curs.execute(db_change("select who, what, time from re_admin where what like ? order by time desc limit ?, 50"), [
                flask.request.args.get('search', 'normal') + "%",
                sql_num
            ])

        get_list = curs.fetchall()
        for data in get_list:
            list_data += '<li>' + ip_pas(data[0]) + ' / ' + html.escape(data[1]) + ' / ' + data[2] + '</li>'

        list_data += '</ul>'
        list_data += next_fix('/admin_log?num=', num, get_list)

        return easy_minify(flask.render_template(skin_check(),
            imp = [load_lang('authority_use_list'), wiki_set(), wiki_custom(), wiki_css([0, 0])],
            data = '''
                <form method="post">
                    <input name="search" id="admin_log_search"> <button type="submit">''' + load_lang('search') + '''</button>
                </form>
                <hr class=\"main_hr\">
            ''' + list_data,
            menu = [['other', load_lang('return')]]
        ))