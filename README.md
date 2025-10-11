# FitTrack – Personal Fitness and Gym Tracker

## Description
FitTrack is a Flask-based web application that helps users track their workouts, meals, weight progress, and personal fitness goals.  
It also provides an AI-based suggestion system (rule-based fallback) to give weekly health and training recommendations.

## Features
- 🏋️‍♂️ Add, edit, and delete workouts  
- 🍽 Log daily meals with calories and macros  
- ⚖️ Track weight and progress charts  
- 🎯 Set and complete fitness goals  
- 🤖 Get weekly personalized advice (rule-based AI Coach)
- 🔐 Login & Register system (Flask-Login)
- 🎨 Clean Tailwind CSS frontend

## Technologies Used
- Python, Flask  
- SQLite, SQLAlchemy  
- Tailwind CSS  
- Chart.js  
- Jinja2 Templates

## How to Run
1. Clone this repository  
   ```bash
   git clone https://github.com/YourGitHubUsername/FitTrack.git
   cd FitTrack
2.Create a virtual environment

bash
Copy code
python -m venv venv
source venv/Scripts/activate   # on Windows: venv\Scripts\activate

3.Install dependencies

bash
Copy code
pip install -r requirements.txt

4.Run the app

bash
Copy code
flask run
Visit http://127.0.0.1:5000
