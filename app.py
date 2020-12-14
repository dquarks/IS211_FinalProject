import json
import flask
import requests
import flask_login

app = flask.Flask(__name__)
app.secret_key = 'abcdefghijklmnop'

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

s_results   = []
t_results   = []

booklist    = []
bookimages  = []
users_db    = {'admin': {'password': 'koolDude123'}}

class User(flask_login.UserMixin):
    pass

@login_manager.unauthorized_handler
def unauthorized_callback():
    return flask.redirect('/login')

@login_manager.user_loader
def user_loader(username):
    if username not in users_db:
        return
    user = User()
    user.id = username
    return user

@login_manager.request_loader
def request_loader(request):
    username = flask.request.form.get('username')
    if username not in users_db:
        return
    user = User()
    user.id = username
    user.is_authenticated = request.form['password'] == users[username]['password']
    return user

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html')

    if flask.request.method == 'POST':
        username = flask.request.form['username']
        if username in users_db:
            if flask.request.form['password'] == users_db[username]['password']:
                user = User()
                user.id = username
                flask_login.login_user(user)
                return flask.redirect(flask.url_for('protected'))
            return 'Bad login credentials: password'
        else:
            return 'Bad login credentials: username'

@app.route('/protected')
@flask_login.login_required
def protected():
    return flask.render_template('index.html', booklist=enumerate(zip(booklist,bookimages)), size=len(booklist), userid=flask_login.current_user.id, search_result=enumerate(s_results))

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect('/login')

@app.route('/search', methods = ['POST'])
def submission():
    del s_results[:]
    del t_results[:]
    search_data = flask.request.form['search_data']
    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + search_data
    if not search_data.isnumeric():
        url = "https://www.googleapis.com/books/v1/volumes?q=" + search_data + "&maxResults=5"
    data = json.loads(requests.get(url).content)

    try:
        if not data["totalItems"]:
            return flask.redirect('/protected')
    except KeyError:
            return flask.redirect('/protected')
    for dump in data["items"]:
        volume_info = dump
        title       = volume_info['volumeInfo']['title']
        authors     = volume_info['volumeInfo'].get('authors','None')
        page_count  = volume_info['volumeInfo'].get('pageCount','0')
        avg_rating  = volume_info['volumeInfo'].get('averageRating', 'None')

        thumb_info  = volume_info['volumeInfo'].get('imageLinks', 'None')
        if thumb_info is not 'None':
            thumb_info = thumb_info['smallThumbnail']
        book_info   = 'Title: ' + title + ' | Author(s): ' + ','.join(authors) + ' | Page Count: ' + str(page_count) + ' | Average Rating: ' + str(avg_rating)
        s_results.append(book_info) # title, author(s), page count, average rating
        t_results.append(thumb_info)
    return flask.redirect('/protected')

@app.route('/add_book', methods = ['GET'])
def add_item():
    this_book   = flask.request.args.get('this_book')
    this_index  = flask.request.args.get('this_index')
    this_thumb  = flask.request.args.get('this_thumb')
    booklist.append(this_book)
    bookimages.append(t_results[(int(this_index))])
    s_results.pop(int(this_index))
    t_results.pop(int(this_index))
    return flask.redirect('/protected')

@app.route('/delete', methods = ['GET'])
def delete_item():
    index = flask.request.args.get('index')
    booklist.pop(int(index))
    bookimages.pop(int(index))
    return flask.redirect('/protected')

if __name__ == '__main__':
    app.run()
