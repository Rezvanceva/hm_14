import json
import sqlite3
import flask


app = flask.Flask(__name__)

def get_value_from_db(sql): #получаем данные из базы по запросу
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        result = connection.execute(sql).fetchall()
    return result

#поиск по названию фильма
def search_by_title(title):
    sql = f'''
            select title, country, release_year, listed_in, description
            from netflix
            where title = '{title}'
            order by release_year desc 
            limit 1'''
    result = get_value_from_db(sql=sql)
    for item in result:
        return dict(item)


@app.get("/movie/<title>/") #по названию фильма
def search_by_title_view(title):
    result = search_by_title(title=title)
    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype="application/json"
    )


@app.get("/movie/<year1>/to/<year2>/")
def search_date_view(year1, year2): #в дипозоне по годам
    sql = f'''
        select title, release_year
        from netflix
        where release_year between '{year1}' and '{year2}'
        limit 100
        '''
    result = []
    for item in get_value_from_db(sql=sql):
        result.append(dict(item))

    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype="application/json"
    )


@app.get("/rating/<rating>/")
def search_raiting_view(rating): #поиск по рейтингу

    dict_of_rating = {
        "children": ("G", "G"),
        "family": ("G", "PG", "PG-13"),
        "adult": ("R", "NC-17")
    }

    sql = f'''
    select title, rating, description
    from netflix
    where rating in {dict_of_rating.get(rating, ("R", "R"))}
    '''

    result = []
    for item in get_value_from_db(sql=sql):
        result.append(dict(item))

    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype="application/json"
    )

@app.get("/genre/<genre>/")
def search_genre_view(genre): #поиск по жанру
    sql = f'''
    select title, description
    from netflix
    where listed_in like '%{genre}'
    order by release_year desc
    limit 10
    '''
    result = []
    for item in get_value_from_db(sql=sql):
        result.append(dict(item))

    return app.response_class(
        response=json.dumps(result, ensure_ascii=False, indent=4),
        status=200,
        mimetype="application/json"
    )

def search_double_name(name1, name2):
    '''возвращает список тех, кто играет с ними в паре больше 2 раз'''

    sql = f'''
    select "cast"
    from netflix
    where "cast" like '%{name1}%' and "cast" like '%{name2}%'
    '''
    result = []
    dict_of_names = {}
    for item in get_value_from_db(sql=sql):
        names = set(dict(item).get('cast').split(",")) - set([name1, name2])
        for name in names:
            dict_of_names[str(name).strip()] = dict_of_names.get(str(name).strip(), 0) + 1


    for key, value in dict_of_names.items():
        if value >= 2:
            result.append(key)
    return result


#задание 6
def get_json_list(movie_type, year, genre):
    sql = f'''
    select title, description, listed_in
    from netflix
    where type = '{movie_type}'
    and release_year = '{year}'
    and listed_in like '%{genre}%'
    '''
    result = []
    for item in get_value_from_db(sql):
        result.append(dict(item))
    return json.dumps(result, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    print(search_double_name('Rose McIver', 'Ben Lamb'))
    print(get_json_list('Movie', '2021', 'Documentaries'))
    app.run(
        host='127.0.0.1',
        port=8080,
        debug=True
    )


