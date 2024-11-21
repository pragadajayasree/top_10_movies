from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


class My_form(FlaskForm):
    edit_rating = StringField(label="New_rating", validators=[DataRequired()])
    edit_review = StringField(label="New_review", validators=[DataRequired()])
    done = SubmitField(label="Done")


class Add_movie(FlaskForm):
    new_movie = StringField("enter movie name", validators=[DataRequired()])
    done = SubmitField(label="Done")


# CREATE DB
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top_movies.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(200), nullable=True)
    img_url: Mapped[str] = mapped_column(String(200), nullable=False)


with app.app_context():
    db.create_all()


# new_movie = Movie(
#             title="Phone Booth",
#             year=2002,
#             description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#             rating=7.3,
#             ranking=10,
#             review="My favourite character was the caller.",
#             img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
#         )
#
#
# second_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )
# with app.app_context():
#     db.session.add(new_movie)
#     db.session.add(second_movie)
#     db.session.commit()


@app.route("/")
def home():
    all_movies = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars().all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()

    return render_template("index.html", movies=all_movies)


@app.route('/find')
def find():
    name = request.args.get("name")
    url = "http://www.omdbapi.com/?"
    parameters = {
        "apikey": "2dfe0e9c",
        "t": name,
    }
    response = requests.get(url=url, params=parameters)
    result = response.json()
    new_movie_add = Movie(
        title=result["Title"],
        year=result["Year"],
        description=result["Plot"],
        rating=result["Ratings"][0]["Value"][0:3],
        img_url=result["Poster"],
    )
    db.session.add(new_movie_add)
    db.session.commit()
    return redirect(url_for('edit1', name=name))


@app.route('/add', methods=["GET", "POST"])
def add():
    form = Add_movie()
    if request.method == "POST":
        url = "http://www.omdbapi.com/?"
        parameters = {
            "apikey": "2dfe0e9c",
            "t": form.new_movie.data,
        }
        response = requests.get(url=url, params=parameters)
        result = response.json()
        return render_template("select.html", list=result)
    return render_template("add.html", form=form)


@app.route('/edit', methods=["GET", "POST"])
def edit():
    my_form = My_form()
    id = request.args.get("id")
    updates = db.get_or_404(Movie, id)
    if request.method == "POST":
        if my_form.validate_on_submit():
            updates.rating = my_form.edit_rating.data
            updates.review = my_form.edit_review.data
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("edit.html", form=my_form, movie=updates)


@app.route("/edit1", methods=["GET", "POST"])
def edit1():
    my_form = My_form()
    name = request.args.get("name")
    updates = Movie.query.filter_by(title=name).first_or_404()
    if request.method == "POST":
        if my_form.validate_on_submit():
            updates.rating = my_form.edit_rating.data
            updates.review = my_form.edit_review.data
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("edit.html", form=my_form, movie=updates)


@app.route('/delete', methods=["GET", "POST"])
def delete():
    id = request.args.get("id")
    del_movie = db.get_or_404(Movie, id)
    db.session.delete(del_movie)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
