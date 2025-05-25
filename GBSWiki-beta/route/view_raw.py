from .tool.func import *

def view_raw_2(conn, name, topic_num, num):
    curs = conn.cursor()

    if acl_check(name, 'render') == 1:
        return re_error('/ban')

    if topic_num:
        topic_num = str(topic_num)

    if not num:
        num = flask.request.args.get('num', None)
        if num:
            num = number_check(num)
    else:
        num = str(num)

    v_name = name
    sub = ' (' + load_lang('raw') + ')'

    if not topic_num and num:
        curs.execute(db_change("select title from history where title = ? and id = ? and hide = 'O'"), [name, num])
        if curs.fetchall() and admin_check(6) != 1:
            return re_error('/error/3')

        curs.execute(db_change("select data from history where title = ? and id = ?"), [name, num])

        sub += ' (r' + num + ')'

        menu = [['history/' + url_pas(name), load_lang('history')]]
    elif topic_num:
        if admin_check(6) != 1:
            curs.execute(db_change("select data from topic where id = ? and code = ? and block = ''"), [num, topic_num])
        else:
            curs.execute(db_change("select data from topic where id = ? and code = ?"), [num, topic_num])

        v_name = load_lang('discussion_raw')
        sub = ' (#' + num + ')'

        menu = [
            ['thread/' + topic_num + '#' + num, load_lang('discussion')], 
            ['thread/' + topic_num + '/admin/' + num, load_lang('return')]
        ]
    else:
        curs.execute(db_change("select data from data where title = ?"), [name])

        menu = [['w/' + url_pas(name), load_lang('return')]]

    data = curs.fetchall()
    if data:
        p_data = html.escape(data[0][0])
        p_data = '<textarea readonly rows="25">' + p_data + '</textarea>'

        return easy_minify(flask.render_template(skin_check(),
            imp = [v_name, wiki_set(), wiki_custom(), wiki_css([sub, 0])],
            data = p_data,
            menu = menu
        ))
    else:
        return re_error('/error/3')