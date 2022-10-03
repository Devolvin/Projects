from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, current_user, login_required, logout_user, AnonymousUserMixin
from flask_bootstrap import Bootstrap
from forms import RegisterForm , LoginForm , CreatePostForm, CommentForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
from datetime import date
from tfidf import calculate_tfidf


app = Flask(__name__)
app.config['SECRET_KEY'] = 'q#f12]4b\J5VVc419F2F]pU'
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
ckeditor = CKEditor(app)

class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.admin_level = 0
    self.id = 0

login_manager.anonymous_user = Anonymous


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Configure tables
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(100))
    # This is for choosing who can post, edit posts, delete posts and stuff
    # Currently on 3 levels
    admin_level = db.Column(db.Integer, nullable=False, default=1)

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="comments")
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    post = relationship("BlogPost", back_populates="comments")
    comment = db.Column(db.Integer, nullable=False)


db.create_all()

@app.route("/")
def index():
    posts = BlogPost.query.all()
    return render_template("index.html", posts=posts)

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        if User.query.filter_by(email=email).first():
            flash("Email is already in use")
            return redirect(url_for("login"))
        if User.query.filter_by(username=username).first():
            flash("Username is already on use")
            return redirect(url_for("register"))
        hashed_pw = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(email=email,
                        username= username,
                        password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("index"))

    return render_template("register.html", form=form)

@app.route('/login', methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if not user:
            return redirect(url_for('login'))
        if not check_password_hash(user.password, form.password.data):
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for("index"))
    return render_template("login.html",form=form)

@login_required
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@login_required
@app.route("/new_post", methods=["GET","POST"])
def add_new_post():
    if current_user.admin_level > 1:
        form = CreatePostForm()
        if form.validate_on_submit():
            new_post = BlogPost(
                title = form.title.data,
                subtitle = form.subtitle.data,
                body = form.body.data,
                author = current_user,
                date = date.today().strftime("%B %d, %Y")
            )
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for("index"))
        return render_template("make_post.html", form=form)


@app.route("/post/<int:post_id>", methods=["GET","POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(
                comment = form.comment.data,
                author_id = current_user.id,
                post_id = post_id
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for("show_post", post_id=post_id))
        else:
            flash("You need to be logged in to comment")
            return redirect(url_for("login"))
    return render_template("post.html",post=requested_post, form=form)

@login_required
@app.route("/edit_post/<int:post_id>", methods=["GET","POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    if current_user.admin_level > 2 or current_user.id == post.author.id:
        edit_form = CreatePostForm(
            title = post.title,
            subtitle = post.subtitle,
            author = post.author,
            body = post.body
        )
        if edit_form.validate_on_submit():
            post.title = edit_form.title.data
            post.subtitle = edit_form.subtitle.data
            post.body = edit_form.body.data
            db.session.commit()
            return redirect(url_for("show_post", post_id=post.id))
        return render_template("make_post.html", form = edit_form, is_edit = True)

@login_required
@app.route("/delete_post/<int:post_id>", methods=["GET","POST"])
def delete_post(post_id):
    post = BlogPost.query.get(post_id)
    if current_user.admin_level > 2 or current_user.id == post.author.id:
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for("index"))
    else:
        abort(401)


@app.route("/question",methods=["GET"])
def question():
    posts = BlogPost.query.all()
    query = request.args.get("query")
    top_post_and_sentence = calculate_tfidf(posts,query)
    if top_post_and_sentence[1][0][3:] == "<p>":
        top_post_and_sentence[1][0] = top_post_and_sentence[1][0][-3:]
    if top_post_and_sentence[1][0][-4:] == "</p>":
        top_post_and_sentence[1][0] =  top_post_and_sentence[1][0][:-4]
    return render_template("post.html", post=top_post_and_sentence[0], sentence=top_post_and_sentence[1][0], query=query)

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(host='localhost', port=5000)