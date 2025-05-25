from .tool.func import *

def search_deep_2(conn, name):
    curs = conn.cursor()

    if name == '':
        return redirect()

    num = int(number_check(flask.request.args.get('num', '1')))
    sql_num = (num * 50 - 50) if num * 50 > 0 else 0

    div = '<ul class="inside_ul">'

    div_plus = ''
    test = ''

    curs.execute(db_change("select title from data where title = ?"), [name])
    link_id = '' if curs.fetchall() else 'id="not_thing"'

    div = '''
        <ul class="inside_ul">
            <li>
                <a ''' + link_id + ' href="/w/' + url_pas(name) + '">' + html.escape(name) + '''</a>
            </li>
        </ul>
        <hr class=\"main_hr\">
        <ul class="inside_ul">
    '''

    curs.execute(db_change('select data from other where name = "count_all_title"'))
    if int(curs.fetchall()[0][0]) < 30000:
        curs.execute(db_change("" + \
            "select distinct title, case " + \
            "when title like ? then 'title' else 'data' end from data " + \
            "where (title like ? or data like ?) order by case " + \
            "when title like ? then 1 else 2 end limit ?, 50"),
            ['%' + name + '%', '%' + name + '%', '%' + name + '%', '%' + name + '%', sql_num]
        )
        all_list = curs.fetchall()
        if all_list:
            test = all_list[0][1]

            for data in all_list:
                if data[1] != test:
                    div_plus += '</ul><hr class=\"main_hr\"><ul class="inside_ul">'

                    test = data[1]

                div_plus += '<li><a href="/w/' + url_pas(data[0]) + '">' + html.escape(data[0]) + '</a> (' + data[1] + ')</li>'
    else:
        curs.execute(db_change("select title from data where title like ? order by title limit ?, 50"),
            ['%' + name + '%', sql_num]
        )
        all_list = curs.fetchall()
        for data in all_list:
            div_plus += '<li><a href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a> (title)</li>'

    div += div_plus + '</ul>'
    div += next_fix('/search/' + url_pas(name) + '?num=', num, all_list)

    return easy_minify(flask.render_template(skin_check(),
        imp = [name, wiki_set(), wiki_custom(), wiki_css(['(' + load_lang('search') + ')', 0])],
        data = div,
        menu = 0
    ))