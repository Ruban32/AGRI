"""
AI-Powered Smart Agriculture System
Main Flask Application
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import joblib
import numpy as np
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'smart_agriculture')
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')

# Initialize MySQL
mysql = MySQL(app)

# Load ML Models
try:
    crop_model = joblib.load('models/crop_recommendation_model.pkl')
    fertilizer_model = joblib.load('models/fertilizer_recommendation_model.pkl')
    yield_model = joblib.load('models/yield_prediction_model.pkl')
    crop_encoder = joblib.load('models/crop_encoder.pkl')
except Exception as e:
    print(f"Warning: Could not load ML models: {e}")

# Weather API Configuration
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', 'your_api_key')
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'


# ==================== ROUTES ====================

# ==================== Authentication Routes ====================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Farmer Registration"""
    message = ''
    
    if request.method == 'POST':
        farmer_name = request.form.get('farmer_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        location = request.form.get('location')
        
        # Validation
        if not all([farmer_name, email, password, confirm_password, phone, location]):
            message = 'Please fill all fields!'
        elif password != confirm_password:
            message = 'Passwords do not match!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        else:
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM farmers WHERE email = %s', (email,))
                account = cursor.fetchone()
                
                if account:
                    message = 'Email already exists!'
                else:
                    hashed_password = generate_password_hash(password)
                    cursor.execute('''
                        INSERT INTO farmers (farmer_name, email, password, phone, location)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (farmer_name, email, hashed_password, phone, location))
                    mysql.connection.commit()
                    message = 'Registration successful! Please login.'
                    return redirect(url_for('login'))
            except Exception as e:
                mysql.connection.rollback()
                message = f'Registration error: {str(e)}'
    
    return render_template('register.html', message=message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Farmer Login"""
    message = ''
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email and password:
            try:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('SELECT * FROM farmers WHERE email = %s', (email,))
                account = cursor.fetchone()
                
                if account and check_password_hash(account['password'], password):
                    session['loggedin'] = True
                    session['farmer_id'] = account['id']
                    session['farmer_name'] = account['farmer_name']
                    session['email'] = email
                    return redirect(url_for('dashboard'))
                else:
                    message = 'Invalid email or password!'
            except Exception as e:
                message = f'Login error: {str(e)}'
        else:
            message = 'Please fill all fields!'
    
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('index'))


# ==================== Dashboard Routes ====================

@app.route('/dashboard')
def dashboard():
    """Farmer Dashboard"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        farmer_id = session['farmer_id']
        
        # Get recent predictions
        cursor.execute('''
            SELECT * FROM predictions 
            WHERE farmer_id = %s 
            ORDER BY created_at DESC LIMIT 10
        ''', (farmer_id,))
        predictions = cursor.fetchall()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) as total FROM predictions WHERE farmer_id = %s', (farmer_id,))
        total_predictions = cursor.fetchone()['total']
        
        return render_template('dashboard.html', 
                             farmer_name=session['farmer_name'],
                             predictions=predictions,
                             total_predictions=total_predictions)
    except Exception as e:
        return f'Error: {str(e)}'


# ==================== Crop Recommendation Routes ====================

@app.route('/crop-recommendation', methods=['GET', 'POST'])
def crop_recommendation():
    """Crop Recommendation Page"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Get input values
            nitrogen = float(data.get('nitrogen', 0))
            phosphorus = float(data.get('phosphorus', 0))
            potassium = float(data.get('potassium', 0))
            ph = float(data.get('ph', 0))
            rainfall = float(data.get('rainfall', 0))
            temperature = float(data.get('temperature', 0))
            humidity = float(data.get('humidity', 0))
            
            # Prepare input for model
            input_features = np.array([[nitrogen, phosphorus, potassium, ph, 
                                       rainfall, temperature, humidity]])
            
            # Make prediction
            prediction = crop_model.predict(input_features)[0]
            confidence = float(crop_model.predict_proba(input_features).max())
            
            # Store in database
            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (farmer_id, prediction_type, input_data, result, confidence, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (session['farmer_id'], 'crop_recommendation',
                  f'N:{nitrogen}, P:{phosphorus}, K:{potassium}, pH:{ph}, Rain:{rainfall}, Temp:{temperature}, Humidity:{humidity}',
                  prediction, confidence, datetime.now()))
            mysql.connection.commit()
            
            return jsonify({
                'success': True,
                'crop': prediction,
                'confidence': f'{confidence*100:.2f}%',
                'message': f'Recommended crop: {prediction}'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    return render_template('crop_recommendation.html', farmer_name=session['farmer_name'])


# ==================== Fertilizer Recommendation Routes ====================

@app.route('/fertilizer-recommendation', methods=['GET', 'POST'])
def fertilizer_recommendation():
    """Fertilizer Recommendation Page"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Get input values
            nitrogen = float(data.get('nitrogen', 0))
            phosphorus = float(data.get('phosphorus', 0))
            potassium = float(data.get('potassium', 0))
            crop = data.get('crop', 'Rice')
            soil_type = data.get('soil_type', 'Loamy')
            moisture = float(data.get('moisture', 0))
            
            # Prepare input for model
            input_features = np.array([[nitrogen, phosphorus, potassium, 
                                       ord(crop[0]), ord(soil_type[0]), moisture]])
            
            # Make prediction
            prediction = fertilizer_model.predict(input_features)[0]
            confidence = float(fertilizer_model.predict_proba(input_features).max())
            
            # Store in database
            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (farmer_id, prediction_type, input_data, result, confidence, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (session['farmer_id'], 'fertilizer_recommendation',
                  f'N:{nitrogen}, P:{phosphorus}, K:{potassium}, Crop:{crop}, Soil:{soil_type}, Moisture:{moisture}',
                  prediction, confidence, datetime.now()))
            mysql.connection.commit()
            
            return jsonify({
                'success': True,
                'fertilizer': prediction,
                'confidence': f'{confidence*100:.2f}%',
                'message': f'Recommended fertilizer: {prediction}'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    return render_template('fertilizer_recommendation.html', farmer_name=session['farmer_name'])


# ==================== Yield Prediction Routes ====================

@app.route('/yield-prediction', methods=['GET', 'POST'])
def yield_prediction():
    """Yield Prediction Page"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Get input values
            crop = data.get('crop', 'Rice')
            area = float(data.get('area', 0))
            rainfall = float(data.get('rainfall', 0))
            temperature = float(data.get('temperature', 0))
            nitrogen = float(data.get('nitrogen', 0))
            phosphorus = float(data.get('phosphorus', 0))
            potassium = float(data.get('potassium', 0))
            
            # Prepare input for model
            input_features = np.array([[ord(crop[0]), area, rainfall, temperature, 
                                       nitrogen, phosphorus, potassium]])
            
            # Make prediction
            prediction = yield_model.predict(input_features)[0]
            confidence = float(yield_model.predict_proba(input_features).max()) if hasattr(yield_model, 'predict_proba') else 0.85
            
            # Store in database
            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (farmer_id, prediction_type, input_data, result, confidence, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (session['farmer_id'], 'yield_prediction',
                  f'Crop:{crop}, Area:{area}, Rain:{rainfall}, Temp:{temperature}, N:{nitrogen}, P:{phosphorus}, K:{potassium}',
                  f'{prediction:.2f} kg/hectare', confidence, datetime.now()))
            mysql.connection.commit()
            
            return jsonify({
                'success': True,
                'yield': f'{prediction:.2f}',
                'unit': 'kg/hectare',
                'confidence': f'{confidence*100:.2f}%',
                'message': f'Predicted yield: {prediction:.2f} kg/hectare'
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    
    return render_template('yield_prediction.html', farmer_name=session['farmer_name'])


# ==================== Weather Routes ====================

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    """Weather Information Page"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    weather_data = None
    error = None
    
    if request.method == 'POST':
        location = request.form.get('location')
        try:
            params = {
                'q': location,
                'appid': WEATHER_API_KEY,
                'units': 'metric'
            }
            response = requests.get(WEATHER_API_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                weather_data = response.json()
            else:
                error = 'Location not found. Please try again.'
        except Exception as e:
            error = f'Error fetching weather data: {str(e)}'
    
    return render_template('weather.html', 
                         farmer_name=session['farmer_name'],
                         weather_data=weather_data,
                         error=error)


# ==================== Prediction History Routes ====================

@app.route('/prediction-history')
def prediction_history():
    """View Prediction History"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT * FROM predictions 
            WHERE farmer_id = %s 
            ORDER BY created_at DESC
        ''', (session['farmer_id'],))
        predictions = cursor.fetchall()
        
        return render_template('prediction_history.html',
                             farmer_name=session['farmer_name'],
                             predictions=predictions)
    except Exception as e:
        return f'Error: {str(e)}'


# ==================== Profile Routes ====================

@app.route('/profile')
def profile():
    """Farmer Profile"""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM farmers WHERE id = %s', (session['farmer_id'],))
        farmer = cursor.fetchone()
        
        return render_template('profile.html',
                             farmer_name=session['farmer_name'],
                             farmer=farmer)
    except Exception as e:
        return f'Error: {str(e)}'


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500


# ==================== Main ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
