# AI-Driven Content Generation and Moderation Bot


1.  https://docs.google.com/document/d/1fOkOMjSE17T92-v4i4zUoS_5DC6mQvYZVdtB4RxQHs8/edit?usp=sharing

2.  https://docs.google.com/document/d/1aGacTNPMwO5s4JfjlRHc2GtnEIEm2fWGNFn3hw3rUYA/edit?usp=sharing

3.  https://docs.google.com/document/d/1-l550kHi9mbzWOw92MgKFrLhgYVAnzB4AiJXqSVDRw0/edit?usp=sharing

4.  https://docs.google.com/document/d/1Vymj17Vk9eznrJq5KJnjkur4nPQImd_SUiIpxKCymiM/edit?usp=sharing


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