from .tool.func import *

def topic_admin_2(conn, topic_num, num):
    curs = conn.cursor()

    num = str(num)
    topic_num = str(topic_num)

    curs.execute(db_change("select block, ip, date from topic where code = ? and id = ?"), [topic_num, num])
    data = curs.fetchall()
    if not data:
        return redirect('/thread/' + topic_num)

    ban = '''
        <h2>''' + load_lang('state') + '''</h2>
        <ul class="inside_ul">
            <li>''' + load_lang('writer') + ' : ''' + ip_pas(data[0][1]) + '''</li>
            <li>''' + load_lang('time') + ' : ' + data[0][2] + '''</li>
        </ul>
        <h2>''' + load_lang('other_tool') + '''</h2>
        <ul class="inside_ul">
            <li>
                <a href="/thread/''' + topic_num + '/raw/' + num + '''">''' + load_lang('raw') + '''</a>
            </li>
        </ul>
    '''

    if admin_check(3) == 1:
        curs.execute(db_change(
            "select id from topic where code = ? and id = ? and top = 'O'"
        ), [topic_num, num])
        top_topic_d = curs.fetchall()

        curs.execute(db_change(
            "select end from rb where block = ? and ongoing = '1'"
        ), [data[0][1]])
        user_ban_d = curs.fetchall()

        ban += '''
            <h2>''' + load_lang('admin_tool') + '''</h2>
            <ul class="inside_ul">
                <li>
                    <a href="/ban/''' + url_pas(data[0][1]) + '''">
                        ''' + (load_lang('release') if user_ban_d else load_lang('ban')) + '''
                    </a>
                </li>
                <li>
                    <a href="/thread/''' + topic_num + '/b/' + num + '''">
                        ''' + (load_lang('hide_release') if data[0][0] == 'O' else load_lang('hide')) + '''
                    </a>
                </li>
                <li>
                    <a href="/thread/''' + topic_num + '/notice/' + num + '''">
                        ''' + (load_lang('pinned_release') if top_topic_d else load_lang('pinned')) + '''
                    </a>
                </li>
            </ul>
        '''

    return easy_minify(flask.render_template(skin_check(),
        imp = [load_lang('discussion_tool'), wiki_set(), wiki_custom(), wiki_css(['(#' + num + ')', 0])],
        data = ban,
        menu = [['thread/' + topic_num + '#' + num, load_lang('return')]]
    ))
