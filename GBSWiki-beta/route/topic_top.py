from .tool.func import *

def topic_top_2(conn, topic_num, num):
    curs = conn.cursor()

    topic_num = str(topic_num)
    num = str(num)

    if admin_check(3, 'notice (code ' + topic_num + '#' + num + ')') != 1:
        return re_error('/error/3')

    curs.execute(db_change("select code from topic where code = ? and id = ?"), [topic_num, num])
    if curs.fetchall():
        curs.execute(db_change("select top from topic where code = ? and id = ?"), [topic_num, num])
        top_data = curs.fetchall()
        if top_data:
            if top_data[0][0] == 'O':
                curs.execute(db_change("update topic set top = '' where code = ? and id = ?"), [topic_num, num])
            else:
                curs.execute(db_change("update topic set top = 'O' where code = ? and id = ?"), [topic_num, num])

        rd_plus(topic_num, get_time())
        conn.commit()

    return redirect('/thread/' + topic_num + '#' + num)
