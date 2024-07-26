# AI-Driven Content Generation and Moderation Bot

## System Design and Architecture

This project is a Flask-based web application that uses Google's Gemini Pro model for AI-driven content generation and moderation. The system consists of the following main components:

- Flask Web Application: Handles routing, user interactions, and integrates all components.
- SQLite Database: Stores user data, posts, comments, and likes.
- Gemini Pro Integration: Provides AI capabilities for content generation and moderation.

### Key Files:
- `app.py`: Main application file containing routes and business logic.
- `models.py`: Defines database models using SQLAlchemy.
- `requirements.txt`: Lists all Python dependencies.
- `wsgi.py`: Entry point for WSGI servers.

## Deployment and Usage Instructions

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup
1. Clone the repository:
   ```
   git clone https://github.com/Kirai-Kevin/AI-Driven-Content-Generation-and-Moderation-Bot-.git
   cd AI-Driven-Content-Generation-and-Moderation-Bot-
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add:
   ```
   SECRET_KEY=your_secret_key
   DATABASE_URI=sqlite:///your_database.db
   GEMINI_API_KEY=your_gemini_api_key
   ```

### Running the Application
1. Initialize the database:
   ```
   python
   >>> from app import create_tables
   >>> create_tables()
   >>> exit()
   ```

2. Start the Flask development server:
   ```
   python app.py
   ```

3. Access the application at `http://localhost:5000`

## Algorithms and Models

### Content Generation
The system uses Google's Gemini Pro model to generate content based on user prompts, desired word count, topic, and mood. The `generate_content` function in `app.py` handles this process.

### Content Moderation
The `moderate_content` and `moderate_comment` functions use Gemini Pro to analyze content for appropriateness, bias, and guideline violations.

### Hashtag and Emoji Generation
The `add_hashtags_and_emojis` function enhances generated content with relevant hashtags and emojis.

## API Documentation

### Routes

#### POST `/post/new`
Creates a new post.
- Request Body:
  - `content`: String
  - `wordCount`: Integer
  - `topic`: String
  - `mood`: String
- Response: Redirects to confirmation page or displays error

#### POST `/post/confirm`
Confirms and publishes a post.
- Request Body:
  - `content`: String
- Response: Redirects to home page or displays error

#### POST `/post/<int:post_id>/comment`
Adds a comment to a post.
- URL Parameters:
  - `post_id`: Integer
- Request Body:
  - `content`: String
- Response: Redirects to home page

#### POST `/post/<int:post_id>/like`
Toggles like on a post.
- URL Parameters:
  - `post_id`: Integer
- Response: Redirects to home page

## Database Schema

### User
- id: Integer (Primary Key)
- username: String (Unique)
- password: String

### Post
- id: Integer (Primary Key)
- content: Text
- timestamp: DateTime
- user_id: Integer (Foreign Key to User)

### Comment
- id: Integer (Primary Key)
- content: Text
- timestamp: DateTime
- user_id: Integer (Foreign Key to User)
- post_id: Integer (Foreign Key to Post)

### Like
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key to User)
- post_id: Integer (Foreign Key to Post)

## Configuration

The application uses environment variables for configuration. Ensure the following variables are set:
- `SECRET_KEY`: Flask secret key
- `DATABASE_URI`: SQLite database URI
- `GEMINI_API_KEY`: API key for Google's Gemini Pro

## Limitations and Potential Improvements

### Current Limitations
- Limited to text-based content generation
- Basic user authentication system
- No real-time updates for likes and comments

### Potential Improvements
- Implement more advanced content moderation techniques like image generation
- Add support for image and video content
- Enhance user profiles with additional features like story, bio, follow
- Implement more robust error handling that offers alternatives
```
