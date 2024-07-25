import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
from dotenv import load_dotenv
from models import db, User, Post, Comment, Like
import random
import emoji
import time
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("No SECRET_KEY set for Flask application")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
if not app.config['SQLALCHEMY_DATABASE_URI']:
    raise ValueError("No DATABASE_URI set for Flask application")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Initialize the database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure the Gemini Pro model
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def add_hashtags_and_emojis(text, topic, mood):
    try:
        # Generate hashtags based on the content
        hashtag_prompt = f"Generate 5 relevant hashtags for this post: {text}"
        hashtag_response = model.generate_content(hashtag_prompt)
        hashtags = hashtag_response.text.split()[:5]  # Take the first 5 hashtags

        # Generate emojis based on the topic and mood
        emoji_prompt = f"Suggest 3 emojis that match the topic '{topic}' and mood '{mood}'"
        emoji_response = model.generate_content(emoji_prompt)
        emojis = emoji_response.text.split()[:3]  # Take the first 3 emojis

        # Add emojis to the beginning of the text
        text = ' '.join(emojis) + ' ' + text

        return text, hashtags
    except Exception as e:
        print(f"Error in add_hashtags_and_emojis: {str(e)}")
        return text, []  # Return original text and empty list if there's an error

def generate_content(prompt, desired_word_count, topic, mood):
    try:
        response = model.generate_content(f"Generate a social media post about: {prompt}. The post should be exactly {desired_word_count} words long. The topic is {topic} and the mood is {mood}.")
        
        if not response.candidates or not response.candidates[0].content:
            if response.candidates and response.candidates[0].safety_ratings:
                safety_issues = [rating.category for rating in response.candidates[0].safety_ratings if rating.probability != "NEGLIGIBLE"]
                if safety_issues:
                    return f"The content could not be generated due to safety concerns related to: {', '.join(safety_issues)}. Please try rephrasing your request."
            
            return "The content could not be generated. Please try again with a different prompt."
        
        generated_text = response.text
        words = generated_text.split()
        
        # Ensure the generated content has exactly the desired word count
        if len(words) > desired_word_count:
            words = words[:desired_word_count]
        elif len(words) < desired_word_count:
            words.extend([''] * (desired_word_count - len(words)))
        
        generated_text = ' '.join(words).strip()
        
        return add_hashtags_and_emojis(generated_text, topic, mood)
    except Exception as e:
        print(f"Error in generate_content: {str(e)}")
        return "An error occurred while generating content. Please try again."
    
def generate_alternative_content(content):
    try:
        prompt = f"Rewrite the following content to be appropriate for a general audience while maintaining the original intent: {content}"
        response = model.generate_content(prompt)
        
        if not response.candidates or not response.candidates[0].content:
            return "Unable to generate alternative content. Please try rephrasing your original post."
        
        return response.text
    except Exception as e:
        print(f"Error in generate_alternative_content: {str(e)}")
        return "An error occurred while generating alternative content. Please try revising your post manually."

def moderate_content(content):
    try:
        prompt = f"Determine if the following content is appropriate for a general audience: {content}. Respond with 'Appropriate' or 'Inappropriate' followed by a brief explanation."
        response = model.generate_content(prompt)
        
        if not response.candidates or not response.candidates[0].content:
            return "Unable to moderate content. Please review your post manually."
        
        return response.text
    except Exception as e:
        print(f"Error in moderate_content: {str(e)}")
        return "An error occurred while moderating content. Please review your post manually."

@app.route('/')
@login_required
def newsfeed():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('newsfeed.html', posts=posts)

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).all()
    return render_template('profile.html', user=user, posts=posts)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        content = request.form['content']
        desired_word_count = int(request.form['wordCount'])
        topic = request.form['topic']
        mood = request.form['mood']
        
        # Generate content based on the user's input and desired word count
        generated_content, hashtags = generate_content(content, desired_word_count, topic, mood)
        
        return render_template('confirm_post.html', 
                               original_content=content, 
                               generated_content=generated_content, 
                               desired_word_count=desired_word_count,
                               hashtags=hashtags)
    return render_template('create_post.html')

@app.route('/post/select_hashtags', methods=['POST'])
@login_required
def select_hashtags():
    content = request.form['content']
    selected_hashtags = request.form.getlist('hashtags')
    
    # Add selected hashtags to the end of the content
    final_content = content + ' ' + ' '.join(selected_hashtags)
    
    # Create and save the post
    post = Post(content=final_content, author=current_user)
    db.session.add(post)
    db.session.commit()
    
    flash('Your post has been created!', 'success')
    return redirect(url_for('newsfeed'))


@app.route('/post/confirm', methods=['POST'])
@login_required
def confirm_post():
    content = request.form['content']
    moderation_result = moderate_content(content)
    
    if 'Appropriate' in moderation_result:
        post = Post(content=content, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('newsfeed'))
    else:
        alternative_content = generate_alternative_content(content)
        return render_template('revise_post.html', original_content=content, alternative_content=alternative_content)

@app.route('/post/revise', methods=['POST'])
@login_required
def revise_post():
    content = request.form['content']
    post = Post(content=content, author=current_user)
    db.session.add(post)
    db.session.commit()
    flash('Your revised post has been created!', 'success')
    return redirect(url_for('newsfeed'))

@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_post(post_id):
    content = request.form['content']
    post = Post.query.get_or_404(post_id)
    comment = Comment(content=content, author=current_user, post=post)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('newsfeed'))

@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user=current_user, post=post).first()
    if like:
        db.session.delete(like)
    else:
        like = Like(user=current_user, post=post)
        db.session.add(like)
    db.session.commit()
    return redirect(url_for('newsfeed'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('newsfeed'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists', 'error')
        else:
            new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('newsfeed'))
    return render_template('signup.html')


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('You do not have permission to delete this post.', 'error')
        return redirect(url_for('profile', username=post.author.username))
    
    # Simulate a delay (remove in production)
    time.sleep(1)
    
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.', 'success')
    return redirect(url_for('profile', username=current_user.username))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()