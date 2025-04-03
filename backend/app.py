from flask import Flask, request, jsonify, Response, send_file
from flask_cors import CORS
import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from config import Config
from utils import parse_gemini_response, validate_symptoms, setup_logging, log_gemini_response, log_debug
from middleware import rate_limit, add_security_headers, validate_request_data
from auth import require_auth, optional_auth, get_current_user_id, is_authenticated
import re
import time
import uuid
import socket
import traceback
from collections import defaultdict, Counter
from pdf_generator import generate_overview_pdf, generate_details_pdf
import tempfile
import shutil
from werkzeug.utils import secure_filename
from datetime import datetime

# Configure logging - reduce verbosity
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.FileHandler("api.log", encoding='utf-8'), logging.StreamHandler()])
logger = logging.getLogger(__name__)

# Configure input logging - separate file for user inputs
input_logger = logging.getLogger("input_logger")
input_logger.setLevel(logging.INFO)
# Use an absolute path for the input log file
current_dir = os.path.dirname(os.path.abspath(__file__))
input_log_path = os.path.join(current_dir, "input.log")
input_file_handler = logging.FileHandler(input_log_path, encoding='utf-8')
input_file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
input_file_handler.setFormatter(input_file_formatter)
input_logger.addHandler(input_file_handler)
# Ensure input logger doesn't propagate to root logger
input_logger.propagate = False

def log_user_input(route, data, ip=None, user_id=None):
    """Log user input data with timestamp and route information"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # Sanitize the data to remove any sensitive information
    sanitized_data = sanitize_data_for_logging(data)
    log_entry = {
        "timestamp": timestamp,
        "route": route,
        "ip_hash": hash_ip(ip) if ip else "unknown",
        "user_id": user_id,
        "data": sanitized_data
    }
    # Use a direct file write approach in addition to the logger
    with open(input_log_path, "a", encoding='utf-8') as f:
        f.write(json.dumps(log_entry) + "\n")
        f.flush()
    # Also log using the logger
    input_logger.info(json.dumps(log_entry))

def sanitize_data_for_logging(data):
    """Remove or mask any sensitive data before logging"""
    if not data:
        return {}
    
    # Create a copy to avoid modifying the original
    sanitized = data.copy() if isinstance(data, dict) else {}
    
    # No sensitive fields in our current data model, but if added later:
    # Example: if 'password' in sanitized: sanitized['password'] = '********'
    
    return sanitized

def hash_ip(ip):
    """Create a hash of the IP address for privacy"""
    import hashlib
    if not ip:
        return "unknown"
    # Add a salt to the hash for security
    salt = "healthvitals-salt"
    return hashlib.sha256((salt + ip).encode()).hexdigest()[:16]

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Configure CORS to allow Authorization header and credentials
CORS(app, 
     origins=["https://healthvitals-ai-43006.web.app/"], 
     supports_credentials=True, 
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
      methods=["GET", "POST", "PUT", "DELETE"])  

setup_logging()

# Setup Google Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logging.error("GEMINI_API_KEY not found in environment variables")
    print("WARNING: GEMINI_API_KEY not found in environment variables")
    # Try to manually read from .env file as a fallback
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    api_key = line.strip().split("=", 1)[1].strip()
                    print(f"Manually loaded API key from .env file: {api_key[:5]}...")
                    break
    except Exception as e:
        print(f"Failed to manually load API key: {str(e)}")

if api_key:
    genai.configure(api_key=api_key)

# Configure safety settings to reduce filtering
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Configure generation settings for Gemini API
generation_config = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 4096,
}

# Track anonymous quick analysis usage by IP
anonymous_quick_analysis_tracker = {}

def has_used_quick_analysis(ip):
    """Check if an anonymous user has already used quick analysis"""
    if ip in anonymous_quick_analysis_tracker:
        return True
    return False

@app.after_request
def after_request(response):
    # Log only HTTP method and path
    logger.info(f"{request.method} {request.path} - Status: {response.status_code}")
    
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return add_security_headers(response)

@app.route('/api/health', methods=['GET'])
def health_check():
    status = {
        "status": "OK",
        "api_key_present": bool(api_key)
    }
    return jsonify(status)

@app.route('/api/analyze-symptoms', methods=['POST'])
@rate_limit
@validate_request_data
@require_auth
def analyze_symptoms():
    try:
        logger.info(f"POST /api/analyze-symptoms - Processing request")
        data = request.get_json()
        
        # Log user input with user ID
        log_user_input("/api/analyze-symptoms", data, request.remote_addr, user_id=request.user_id)
        
        # Only log minimal information, not the entire request
        symptoms = data.get('symptoms', [])
        age = data.get('age', '')
        gender = data.get('gender', '')
        height = data.get('height', '')
        weight = data.get('weight', '')
        medical_history = data.get('medicalHistory', [])
        medical_history_text = data.get('medicalHistoryText', '')
        
        # Get lifestyle factors
        exercise_frequency = data.get('exerciseFrequency', 'moderate')
        sleep_quality = data.get('sleepQuality', 'fair')
        stress_level = data.get('stressLevel', 'moderate')
        
        logger.info(f"Analyzing {len(symptoms)} symptoms with lifestyle factors")
        
        # Convert severity to integers if they are strings
        for symptom in symptoms:
            if 'severity' in symptom and isinstance(symptom['severity'], str):
                try:
                    symptom['severity'] = int(symptom['severity'])
                except (ValueError, TypeError):
                    symptom['severity'] = 5  # Default to medium severity

        # Validate symptoms data
        validation_result = validate_symptoms(symptoms)
        if not validation_result['valid']:
            logger.error(f"Symptom validation failed: {validation_result['message']}")
            return jsonify({"error": validation_result['message']}), 400

        if not api_key:
            logger.error("Cannot process request: GEMINI_API_KEY not configured")
            return jsonify({
                "error": "API key not configured",
                "recommendation": "Please check server configuration"
            }), 500
        
        # Format symptoms for the prompt
        formatted_symptoms = "\n".join([f"- {s['name']} (Severity: {s['severity']}/10, Duration: {s['duration']})" for s in symptoms])
        formatted_medical_history = "\n".join([f"- {condition}" for condition in medical_history]) if medical_history else "None"
        
        # Get additional details from the request
        diet_preference = data.get('dietPreference', 'balanced')
        current_medications = data.get('currentMedications', '')
        allergies = data.get('allergies', '')
        recent_life_changes = data.get('recentLifeChanges', '')
        
        logger.info(f"Calling Gemini API for analysis")
        
        # Create the prompt for Gemini
        prompt = f"""
        Analyze the following symptoms as a medical AI assistant. Provide a comprehensive medical analysis based on the symptoms, age, gender, height, weight, medical history, lifestyle factors, and additional details provided.

        PATIENT INFORMATION:
        Age: {age}
        Gender: {gender}
        Height: {height} cm
        Weight: {weight} kg
        Symptoms: 
        {formatted_symptoms}
        Medical History: 
        {formatted_medical_history}
        
        Additional Medical History (in patient's own words):
        {medical_history_text}
        
        LIFESTYLE FACTORS:
        Exercise Frequency: {exercise_frequency}
        Sleep Quality: {sleep_quality}
        Stress Level: {stress_level}
        
        Diet Preference: {diet_preference}
        Current Medications: {current_medications if current_medications else "None reported"}
        Allergies: {allergies if allergies else "None reported"}
        Recent Life Changes: {recent_life_changes if recent_life_changes else "None reported"}
        
        Please provide a comprehensive analysis with EACH section clearly separated by its own heading. 
        Use the EXACT section headings below - do not combine or merge sections:
        
        POSSIBLE CONDITIONS:
        YOU MUST LIST EXACTLY 5 POTENTIAL CONDITIONS. No more, no less.
        Each condition should have its own probability percentage (0-100%).
        Format: 
        1. Condition Name (Probability: XX%): Brief description of the condition.
        2. Condition Name (Probability: XX%): Brief description of the condition.
        3. Condition Name (Probability: XX%): Brief description of the condition.
        4. Condition Name (Probability: XX%): Brief description of the condition.
        5. Condition Name (Probability: XX%): Brief description of the condition.
        
        TAKE INTO ACCOUNT THE PATIENT'S LIFESTYLE FACTORS AND MEDICAL HISTORY (including the text-based medical history) when determining conditions and probabilities.
        
        IMMEDIATELY after each condition, include these subsections with specific recommendations:
        
        [CONDITION_NAME] RECOMMENDED ACTIONS:
        1. [Specific action for this condition]
        2. [Specific action for this condition]
        3. [Specific action for this condition]
        4. [Specific action for this condition]
        5. [Specific action for this condition]
        
        [CONDITION_NAME] PREVENTIVE MEASURES:
        1. [Specific preventive measure for this condition]
        2. [Specific preventive measure for this condition]
        3. [Specific preventive measure for this condition]
        4. [Specific preventive measure for this condition]
        5. [Specific preventive measure for this condition]
        
        Example structure:
        1. Migraine (Probability: 75%): A neurological condition...
        
        MIGRAINE RECOMMENDED ACTIONS:
        1. Rest in a dark, quiet room
        2. Apply cold compresses to forehead
        3. Take prescribed migraine medication
        
        MIGRAINE PREVENTIVE MEASURES:
        1. Identify and avoid personal triggers
        2. Maintain regular sleep schedule
        3. Stay hydrated
        
        2. [Next condition with same format...]
        
        RECOMMENDATION:
        Give an overall recommendation for the patient.
        
        URGENCY LEVEL:
        Specify urgency as 'low', 'medium', or 'high' - one word only.
        
        FOLLOW-UP ACTIONS:
        List 3-5 recommended next steps, each on a new line with a number.
        Include specific advice related to the patient's lifestyle factors, medical history (both structured and text-based), allergies, recent life changes and current medications, and symptoms, height, weight, age, gender, where applicable.
        
        RISK FACTORS:
        List 3-5 potential risk factors based on the symptoms and lifestyle factors, and medical history (both structured and text-based), and allergies, and recent life changes and current medications, and symptoms, height, weight, age, gender, each on a new line with a number.
        
        INDIAN MEAL RECOMMENDATIONS:
        Suggest specific Indian meals based on the patient's diet preference ({diet_preference}), and medical history ({formatted_medical_history}), and lifestyle factors ({exercise_frequency}), and allergies ({allergies}), and recent life changes ({recent_life_changes}) and current medications ({current_medications}), and symptoms ({formatted_symptoms}) with severity and additional medical history ({medical_history_text}), and height ({height}), and weight ({weight}), and age ({age}), each on a new line with a number.
        Organize in three clearly labeled sections:
        Breakfast: List 5 meal options with its ingredients, total calories in that meal, micro and macro nutrients and benefits, each on a new line with a number.
        Lunch: List 5 meal options with its ingredients, total calories in that meal, micro and macro nutrients and benefits, each on a new line with a number.
        Dinner: List 5 meal options with its ingredients, total calories in that meal, micro and macro nutrients and benefits, each on a new line with a number.
        
        IMPORTANT: If patient has allergies specific medical history and symptoms and additional medical history then avoid those foods in recommendations.
        At the end of this section, add: "These meal recommendations are based on your {diet_preference} diet preference."
        
        EXERCISE PLAN:
        List 3-5 recommended exercises or physical activities based on the current exercise frequency ({exercise_frequency}), and medical history ({medical_history} and text-based history), and managing stress levels ({stress_level}), and allergies ({allergies}), and recent life changes ({recent_life_changes}) and current medications ({current_medications}), and symptoms ({formatted_symptoms}) with severity and height ({height}), and weight ({weight}), and age ({age}), each on a new line with a number.
        
        POSSIBLE DISEASES:
        List 3-5 potential diseases associated with these symptoms, each on a new line with a number.
        
        PREVENTIVE MEASURES:
        List 3-5 preventive measures, especially focusing on improving sleep quality ({sleep_quality}) and managing stress levels ({stress_level}), and diet preference ({diet_preference}), and medical history ({formatted_medical_history}), and lifestyle factors ({exercise_frequency}), and allergies ({allergies}), and recent life changes ({recent_life_changes}) and current medications ({current_medications}), and symptoms ({formatted_symptoms}) with severity and height ({height}), and weight ({weight}), and age ({age}), each on a new line with a number.
        
        AYURVEDIC MEDICATION:
        Provide 5 specific Ayurvedic recommendations structured as follows (include exactly 5 recommendations, each with all requested details):
        
        1. [Ayurvedic Medicine/Herb/Treatment Name]
           - Description: Detailed paragraph of 5-6 lines describing this specific Ayurvedic approach and how it relates to the patient's symptoms, medical history (both structured and text-based), height, weight, and lifestyle factors.
           - Importance: Detailed paragraph of 5-6 lines explaining why this specific Ayurvedic approach is important for this patient's condition.
           - Benefits: Detailed paragraph of 5-6 lines explaining the specific benefits of this Ayurvedic recommendation for the patient's condition and symptoms.
        
        2. [Ayurvedic Medicine/Herb/Treatment Name]
           - Description: Detailed paragraph of 5-6 lines describing this specific Ayurvedic approach and how it relates to the patient's symptoms, medical history (both structured and text-based), height, weight, and lifestyle factors.
           - Importance: Detailed paragraph of 5-6 lines explaining why this specific Ayurvedic approach is important for this patient's condition.
           - Benefits: Detailed paragraph of 5-6 lines explaining the specific benefits of this Ayurvedic recommendation for the patient's condition and symptoms.
        
        3. [Ayurvedic Medicine/Herb/Treatment Name]
           - Description: Detailed paragraph of 5-6 lines describing this specific Ayurvedic approach and how it relates to the patient's symptoms, medical history (both structured and text-based), height, weight, and lifestyle factors.
           - Importance: Detailed paragraph of 5-6 lines explaining why this specific Ayurvedic approach is important for this patient's condition.
           - Benefits: Detailed paragraph of 5-6 lines explaining the specific benefits of this Ayurvedic recommendation for the patient's condition and symptoms.
        
        4. [Ayurvedic Medicine/Herb/Treatment Name]
           - Description: Detailed paragraph of 5-6 lines describing this specific Ayurvedic approach and how it relates to the patient's symptoms, medical history (both structured and text-based), height, weight, and lifestyle factors.
           - Importance: Detailed paragraph of 5-6 lines explaining why this specific Ayurvedic approach is important for this patient's condition.
           - Benefits: Detailed paragraph of 5-6 lines explaining the specific benefits of this Ayurvedic recommendation for the patient's condition and symptoms.
        
        5. [Ayurvedic Medicine/Herb/Treatment Name]
           - Description: Detailed paragraph of 5-6 lines describing this specific Ayurvedic approach and how it relates to the patient's symptoms, medical history (both structured and text-based), height, weight, and lifestyle factors.
           - Importance: Detailed paragraph of 5-6 lines explaining why this specific Ayurvedic approach is important for this patient's condition.
           - Benefits: Detailed paragraph of 5-6 lines explaining the specific benefits of this Ayurvedic recommendation for the patient's condition and symptoms.
        
        DO'S:
        List 3-5 things the patient should do, with emphasis on lifestyle improvements related to exercise, sleep, and stress management, and diet preference, and medical history (both structured and text-based), and lifestyle factors, and allergies, and recent life changes and current medications, and symptoms, height, weight, age, gender, each on a new line with a number.
        
        DON'TS:
        List 3-5 things the patient should avoid, particularly behaviors that could worsen their stress level and sleep quality, and diet preference, and medical history (both structured and text-based), and lifestyle factors, and allergies, and recent life changes and current medications, and symptoms, height, weight, age, gender, each on a new line with a number.
        
        REPORTS REQUIRED:
        Recommend 3-5 specific diagnostic tests or medical reports the patient should obtain based on their symptoms and medical history (both structured and text-based), and symptoms, height, weight, age, gender.
        
        YOU MUST FORMAT EACH REPORT EXACTLY AS FOLLOWS with clear section markers:
        
        1. [Test/Report Name]
           - Purpose: [4-5 detailed bullet points about why this test is needed]
           - Benefits: [4-5 detailed bullet points about the benefits of this test]  
           - Analysis Details: [4-5 detailed bullet points about what this test measures]
           - Preparation Required: [4-5 detailed bullet points about how to prepare for this test]
           - Recommendation Reason: [4-5 detailed bullet points about why you're recommending this test]
        
        2. [Next Test/Report Name]
           - Purpose: [4-5 detailed bullet points about why this test is needed]
           - Benefits: [4-5 detailed bullet points about the benefits of this test]
           - Analysis Details: [4-5 detailed bullet points about what this test measures]
           - Preparation Required: [4-5 detailed bullet points about how to prepare for this test]
           - Recommendation Reason: [4-5 detailed bullet points about why you're recommending this test]
           
        CRITICAL FORMATTING REQUIREMENTS FOR REPORTS:
        - Each report MUST be numbered (1., 2., etc.)
        - Each report MUST have all five subsections with EXACTLY these labels: "- Purpose:", "- Benefits:", "- Analysis Details:", "- Preparation Required:", and "- Recommendation Reason:"
        - Each subsection MUST start with a dash followed by the label and a colon, exactly as shown above
        - Each report must be separated clearly from others
        - Each subsection must contain multiple detailed bullet points (not just a single paragraph)
        
        HEALTH SCORE:
        Provide a numerical health score from 1-10 (where 10 is perfectly healthy) based on the symptoms, lifestyle factors, and medical history provided (both structured and text-based) and all other information provided by the patient. Include a brief one-sentence explanation for this score.
        Format: [Score]/10 - [Brief explanation]
        
        IMPORTANT FORMATTING RULES:
        1. Use ONLY the EXACT section headings provided above.
        2. Each section MUST have its own clear heading.
        3. DO NOT use asterisks (*) anywhere in your response.
        4. Number each list item (1., 2., 3., etc.).
        5. Keep each section separate - do not combine multiple sections into one.
        6. Ensure the POSSIBLE CONDITIONS section includes clear probability percentages.
        7. For INDIAN MEAL RECOMMENDATIONS, clearly label Breakfast, Lunch, and Dinner subsections.
        8. Include a professional tone with clear advice.
        9. Consider the patient's reported allergies, medications, and lifestyle factors in your recommendations.
        10. For each condition, include condition-specific recommended actions and preventive measures.
        """

        try:
            # Create model and specify parameters
            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config={
                    "temperature": 0.4,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 4096,
                },
                safety_settings=safety_settings
            )
            
            response = model.generate_content(prompt)
            
            logger.info("Received Gemini API response and processing results")
            
            # Log the raw Gemini response in a single line format
            response_id = f"analyze_{int(time.time())}"
            log_gemini_response(response_id, response.text)
            
            # Parse and structure the response
            result = parse_gemini_response(response.text)
            
            # Log only key stats about the result, not the entire content
            logger.info(f"Analysis complete - Found {len(result['possibleConditions'])} conditions with urgency: {result['urgency']}")
            
            return jsonify(result)
        except Exception as api_error:
            logger.error(f"Error calling Gemini API: {str(api_error)}")
            # Check if this is a quota error
            error_message = str(api_error)
            if "429" in error_message and "quota" in error_message.lower():
                return jsonify({
                    "possibleConditions": [
                        {
                            "name": "API Quota Exceeded",
                            "probability": 100,
                            "description": "The Google Gemini API quota has been exhausted. Please try again later or update your API key.",
                            "category": "error"
                        }
                    ],
                    "recommendation": "The system is currently experiencing high demand. Please try again later or contact support for assistance.",
                    "urgency": "medium",
                    "followUpActions": ["Try again later", "Contact support", "Consider updating the API key"],
                    "riskFactors": ["Unable to analyze symptoms due to API limitations"],
                    "mealRecommendations": {"breakfast": [], "lunch": [], "dinner": []},
                    "exercisePlan": [],
                    "diseases": [],
                    "preventiveMeasures": ["Consider using the offline symptom checker as an alternative"],
                    "ayurvedicMedication": {
                        "recommendations": [
                            {
                                "name": "Ayurvedic Consultation",
                                "description": "A qualified Ayurvedic practitioner would be able to provide personalized recommendations based on your doshas and current health condition. Due to API limitations, specific Ayurvedic recommendations cannot be provided at this time.",
                                "importance": "Ayurvedic medicine is highly personalized and should be prescribed by trained practitioners who can analyze your specific constitution and imbalances.",
                                "benefits": "Consulting with an Ayurvedic practitioner offers numerous benefits including a personalized treatment approach based on your unique constitution (prakriti), a holistic assessment that considers not just physical symptoms but your mental and emotional wellbeing, and access to safe, time-tested herbal formulations that can complement conventional medicine. Additionally, Ayurvedic treatments often focus on lifestyle modifications and dietary recommendations that address the root cause of your condition rather than just managing symptoms."
                            }
                        ]
                    },
                    "dos": ["Contact healthcare provider for urgent concerns"],
                    "donts": ["Don't rely solely on automated analysis"]
                })
            # Provide default response in case of API error
            return jsonify({
                "possibleConditions": [
                    {
                        "name": "API Error",
                        "probability": 100,
                        "description": f"Unable to analyze symptoms: {str(api_error)}",
                        "category": "error"
                    }
                ],
                "recommendation": "Please try again later or consult a healthcare professional directly.",
                "urgency": "medium",
                "followUpActions": ["Try again later", "Consult a healthcare professional"],
                "riskFactors": ["Unable to analyze symptoms properly"],
                "mealRecommendations": {"breakfast": [], "lunch": [], "dinner": []},
                "exercisePlan": [],
                "diseases": [],
                "preventiveMeasures": ["Consult a healthcare professional"],
                "ayurvedicMedication": {
                    "recommendations": [
                        {
                            "name": "Ayurvedic Consultation",
                            "description": "A qualified Ayurvedic practitioner would be able to provide personalized recommendations based on your doshas and current health condition. Due to API limitations, specific Ayurvedic recommendations cannot be provided at this time.",
                            "importance": "Ayurvedic medicine is highly personalized and should be prescribed by trained practitioners who can analyze your specific constitution and imbalances.",
                            "benefits": "Consulting with an Ayurvedic practitioner offers numerous benefits including a personalized treatment approach based on your unique constitution (prakriti), a holistic assessment that considers not just physical symptoms but your mental and emotional wellbeing, and access to safe, time-tested herbal formulations that can complement conventional medicine. Additionally, Ayurvedic treatments often focus on lifestyle modifications and dietary recommendations that address the root cause of your condition rather than just managing symptoms."
                        }
                    ]
                },
                "dos": ["Consult a healthcare professional"],
                "donts": ["Don't rely solely on automated analysis"]
            })

    except Exception as e:
        logger.error(f"Error in analyze_symptoms: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/quick-analyze', methods=['POST'])
@rate_limit
@validate_request_data
@optional_auth
def quick_analyze():
    try:
        logger.info(f"POST /api/quick-analyze - Processing request")
        data = request.get_json()
        
        # Get client IP
        client_ip = request.remote_addr
        
        # Track if this is an anonymous user's first request
        user_id = get_current_user_id()
        is_first_request = True
        
        # If not authenticated, check if they've used quick analysis before
        if user_id is None:
            is_first_request = not has_used_quick_analysis(client_ip)
            if is_first_request:
                # Mark this IP as having used quick analysis
                anonymous_quick_analysis_tracker[client_ip] = time.time()
        
        # Log user input
        log_user_input("/api/quick-analyze", data, client_ip, user_id=user_id)
        
        # Get basic information
        symptoms_description = data.get('symptoms', '')
        age = data.get('age', '')
        
        logger.info(f"Quick analyzing symptoms for age: {age}")
        
        if not symptoms_description:
            logger.error("No symptoms provided")
            return jsonify({"error": "Please provide symptoms"}), 400

        if not api_key:
            logger.error("Cannot process request: GEMINI_API_KEY not configured")
            return jsonify({
                "error": "API key not configured",
                "recommendation": "Please check server configuration"
            }), 500
        
        logger.info(f"Calling Gemini API for quick analysis")
        
        # Create the prompt for Gemini - simplified version
        prompt = f"""
        As a medical AI assistant, analyze the following symptoms briefly:

        PATIENT INFORMATION:
        Age: {age}
        Symptoms: {symptoms_description}
        
        Please provide a brief analysis with EACH section clearly separated:
        
        POSSIBLE CONDITIONS:
        List 3-5 potential conditions that could explain these symptoms, from most to least likely.
        Format each as a simple name without percentages.
        
        RECOMMENDATION:
        Give a single paragraph recommendation for the patient.
        
        URGENCY LEVEL:
        Specify urgency as 'low', 'medium', or 'high' - one word only.
        
        DO NOT include any other sections and keep the analysis brief and focused.
        DO NOT use asterisks (*) anywhere in your response.
        """

        try:
            # Create model and specify parameters
            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config={
                    "temperature": 0.4,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                },
                safety_settings=safety_settings
            )
            
            response = model.generate_content(prompt)
            
            logger.info("Received Gemini API response for quick analysis")
            
            # Log the raw Gemini response in a single line format
            response_id = f"quick_{int(time.time())}"
            log_gemini_response(response_id, response.text)
            
            # Parse the quick response
            response_text = response.text
            
            # Log the start of parsing
            log_debug("Starting to parse quick analysis response")
            
            # Extract possible conditions
            conditions_match = re.search(r'POSSIBLE CONDITIONS:(.*?)(?=RECOMMENDATION:|$)', response_text, re.DOTALL | re.IGNORECASE)
            conditions_text = conditions_match.group(1).strip() if conditions_match else ""
            
            log_debug("Found conditions section for quick analysis", {
                "content_length": len(conditions_text),
                "first_50_chars": conditions_text[:50] if conditions_text else "None"
            })
            
            # Extract conditions list items
            conditions = []
            try:
                # Try different regex patterns to match the list items
                # Pattern 1: Look for numbered list with format "1. Item"
                condition_items = re.findall(r'(?:^|\n)(?:\d+\.\s*)([^\n]+)', conditions_text)
                
                # Pattern 2: If no matches, try looking for plain lines
                if not condition_items:
                    condition_items = [line.strip() for line in conditions_text.split('\n') if line.strip()]
                
                for item in condition_items:
                    conditions.append(item.strip())
                
                log_debug("Extracted quick analysis conditions", {
                    "count": len(conditions),
                    "conditions": conditions
                })
            except Exception as e:
                log_debug("Error extracting conditions", {"error": str(e)})
            
            # If still no conditions extracted, provide defaults
            if not conditions:
                log_debug("No conditions found, using defaults")
                conditions = ["Symptom analysis inconclusive"]
            
            # Extract recommendation
            recommendation = ""
            try:
                recommendation_match = re.search(r'RECOMMENDATION:(.*?)(?=URGENCY LEVEL:|$)', response_text, re.DOTALL | re.IGNORECASE)
                recommendation = recommendation_match.group(1).strip() if recommendation_match else ""
                
                log_debug("Extracted quick analysis recommendation", {
                    "length": len(recommendation),
                    "first_50_chars": recommendation[:50] if recommendation else "None"
                })
            except Exception as e:
                log_debug("Error extracting recommendation", {"error": str(e)})
            
            # If no recommendation found, provide a default
            if not recommendation:
                recommendation = "Please consult a healthcare professional for a proper diagnosis."
                log_debug("Using default recommendation")
            
            # Extract urgency level
            urgency = "medium"  # Default
            try:
                urgency_match = re.search(r'URGENCY LEVEL:(.*?)(?=$)', response_text, re.DOTALL | re.IGNORECASE)
                urgency_text = urgency_match.group(1).strip().lower() if urgency_match else "medium"
                
                # Normalize urgency to one of three values
                if 'high' in urgency_text:
                    urgency = "high"
                elif 'medium' in urgency_text or 'moderate' in urgency_text:
                    urgency = "medium"
                else:
                    urgency = "low"
                
                log_debug("Extracted quick analysis urgency", {
                    "raw_urgency": urgency_text,
                    "normalized_urgency": urgency
                })
            except Exception as e:
                log_debug("Error extracting urgency", {"error": str(e)})
            
            # Add is_anonymous_first_request to the result
            result = {
                "possibleConditions": conditions,
                "recommendation": recommendation,
                "urgency": urgency,
                "is_anonymous_first_request": is_first_request
            }
            
            log_debug("Quick analysis parsing complete", {
                "conditions_count": len(conditions),
                "urgency": urgency
            })
            
            logger.info(f"Quick analysis complete - Found {len(conditions)} conditions with urgency: {urgency}")
            
            return jsonify(result)
        except Exception as api_error:
            logger.error(f"Error calling Gemini API: {str(api_error)}")
            # Check if this is a quota error
            error_message = str(api_error)
            if "429" in error_message and "quota" in error_message.lower():
                return jsonify({
                    "possibleConditions": ["API Quota Exceeded"],
                    "recommendation": "The Google Gemini API quota has been exhausted. Please try again later or update your API key.",
                    "urgency": "medium"
                })
            # Provide default response in case of API error
            return jsonify({
                "possibleConditions": ["API Error - Unable to analyze symptoms"],
                "recommendation": "Please try again later or consult a healthcare professional directly.",
                "urgency": "medium"
            })

    except Exception as e:
        logger.error(f"Error in quick_analyze: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-overview-pdf', methods=['POST'])
@require_auth
def generate_overview_pdf_endpoint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Log request for debugging
        logger.info(f"Generating overview PDF report")
        
        # Generate the PDF using the utility
        pdf_buffer = generate_overview_pdf(data)
        
        # Return the PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='healthvitals-overview-report.pdf'
        )
    except Exception as e:
        logger.error(f"Error generating overview PDF: {str(e)}")
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500


@app.route('/api/generate-details-pdf', methods=['POST'])
@require_auth
def generate_details_pdf_endpoint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Log request for debugging
        logger.info(f"Generating detailed PDF report")
        
        # Generate the PDF using the utility
        pdf_buffer = generate_details_pdf(data)
        
        # Return the PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='healthvitals-detailed-report.pdf'
        )
    except Exception as e:
        logger.error(f"Error generating detailed PDF: {str(e)}")
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

# New endpoints that don't require authentication for PDF generation
@app.route('/api/public/generate-overview-pdf', methods=['POST'])
@rate_limit
@validate_request_data
def generate_overview_pdf_public():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Log request for debugging
        logger.info(f"Generating public overview PDF report")
        
        # Generate the PDF using the utility
        pdf_buffer = generate_overview_pdf(data)
        
        # Return the PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='healthvitals-overview-report.pdf'
        )
    except Exception as e:
        logger.error(f"Error generating public overview PDF: {str(e)}")
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500


@app.route('/api/public/generate-details-pdf', methods=['POST'])
@rate_limit
@validate_request_data
def generate_details_pdf_public():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Log request for debugging
        logger.info(f"Generating public detailed PDF report")
        
        # Generate the PDF using the utility
        pdf_buffer = generate_details_pdf(data)
        
        # Return the PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='healthvitals-detailed-report.pdf'
        )
    except Exception as e:
        logger.error(f"Error generating public detailed PDF: {str(e)}")
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

@app.route('/api/analyze-reports', methods=['POST'])
@rate_limit
def analyze_reports():
    try:
        logger.info("Starting report analysis...")
        
        # Check if files were uploaded
        if 'reports' not in request.files:
            logger.error("No files found in the request")
            return jsonify({"error": "No files uploaded"}), 400
        
        # Get all uploaded files
        files = request.files.getlist('reports')
        
        if not files or len(files) == 0:
            logger.error("Empty file list received")
            return jsonify({"error": "No files uploaded"}), 400
        
        logger.info(f"Received {len(files)} files: {', '.join([f.filename for f in files if f.filename])}")
        
        # Get the analysis result and symptoms for context
        try:
            analysis_result = json.loads(request.form.get('analysisResult', '{}'))
            selected_symptoms = json.loads(request.form.get('selectedSymptoms', '[]'))
            logger.info(f"Successfully parsed analysis_result and selected_symptoms from request")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from request: {str(e)}")
            return jsonify({"error": "Invalid JSON data in request"}), 400
        
        logger.info(f"Analyzing {len(files)} medical reports")
        
        # Create a temporary directory to store uploaded files
        temp_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        os.makedirs(temp_dir, exist_ok=True)
        logger.info(f"Created temporary directory: {temp_dir}")
        
        try:
            # Process and save each file
            file_paths = []
            for file in files:
                if file.filename:
                    try:
                        # Create a secure filename
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(temp_dir, filename)
                        file.save(filepath)
                        file_size = os.path.getsize(filepath) / 1024  # KB
                        logger.info(f"Saved file: {filename} ({file_size:.1f} KB)")
                        file_paths.append(filepath)
                    except Exception as file_err:
                        logger.error(f"Error saving file {file.filename}: {str(file_err)}")
            
            if not file_paths:
                logger.error("No files were successfully saved")
                return jsonify({"error": "Failed to process uploaded files"}), 400
            
            logger.info(f"Successfully saved {len(file_paths)} files, generating prompt...")
            
            # Analyze the medical reports using Gemini API
            prompt = create_report_analysis_prompt(file_paths, analysis_result, selected_symptoms)
            logger.info("Generated prompt for Gemini API, sending request...")
            
            report_analysis = analyze_medical_reports_with_gemini(prompt)
            logger.info("Successfully received and parsed response from Gemini API")
            
            # Clean up temporary files
            for file_path in file_paths:
                if os.path.exists(file_path):
                    os.remove(file_path)
            os.rmdir(temp_dir)
            logger.info("Cleaned up temporary files")
            
            return jsonify(report_analysis)
        except Exception as e:
            logger.error(f"Error during report analysis: {str(e)}")
            logger.error(f"Exception traceback: {traceback.format_exc()}")
            # Ensure cleanup in case of errors
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.info("Cleaned up temporary directory after error")
                except Exception as cleanup_err:
                    logger.error(f"Error cleaning up temp dir: {str(cleanup_err)}")
            raise e
    except Exception as e:
        logger.error(f"Error analyzing reports: {str(e)}")
        logger.error(f"Exception traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Failed to analyze reports: {str(e)}"}), 500


# Helper function to create a prompt for the Gemini API based on reports and context
def create_report_analysis_prompt(file_paths, analysis_result, selected_symptoms):
    # Extract comprehensive user information
    age = analysis_result.get('age', 'Not provided')
    gender = analysis_result.get('gender', 'Not provided')
    height = analysis_result.get('height', 'Not provided')
    weight = analysis_result.get('weight', 'Not provided')
    medical_history = analysis_result.get('medicalHistory', [])
    medical_history_text = analysis_result.get('medicalHistoryText', '')
    
    # Lifestyle factors
    exercise_frequency = analysis_result.get('exerciseFrequency', 'Not provided')
    sleep_quality = analysis_result.get('sleepQuality', 'Not provided')
    stress_level = analysis_result.get('stressLevel', 'Not provided')
    diet_preference = analysis_result.get('dietPreference', 'Not provided')
    allergies = analysis_result.get('allergies', 'Not provided')
    current_medications = analysis_result.get('currentMedications', 'Not provided')
    recent_life_changes = analysis_result.get('recentLifeChanges', 'Not provided')
    
    # Format patient profile
    patient_profile = f"""
    Patient Profile:
    - Age: {age}
    - Gender: {gender}
    - Height: {height}
    - Weight: {weight}
    - Exercise Frequency: {exercise_frequency}
    - Sleep Quality: {sleep_quality}
    - Stress Level: {stress_level}
    - Diet Preference: {diet_preference}
    - Allergies: {allergies}
    - Current Medications: {current_medications}
    - Recent Life Changes: {recent_life_changes}
    """
    
    # Format medical history
    medical_history_formatted = "Medical History:\n"
    if medical_history:
        medical_history_formatted += "\n".join([f"- {condition}" for condition in medical_history])
    elif medical_history_text:
        medical_history_formatted += medical_history_text
    else:
        medical_history_formatted += "None reported"
    
    # Format symptoms
    symptoms_text = "Symptoms reported by patient:\n"
    for symptom in selected_symptoms:
        symptoms_text += f"- {symptom['name']} (Severity: {symptom['severity']}/10, Duration: {symptom['duration']})\n"
    
    # Format initial analysis
    conditions_text = "Initial analysis suggested these conditions:\n"
    for condition in analysis_result.get('possibleConditions', []):
        conditions_text += f"- {condition['name']} ({condition['probability']}% probability): {condition.get('description', '')}\n"
    
    recommendations_text = "Initial recommendations:\n" + analysis_result.get('recommendation', 'None provided')
    
    # Count file types for better guidance to the model
    image_count = 0
    pdf_count = 0
    doc_count = 0
    
    # Format uploaded files info
    files_info = "Uploaded medical reports summary:\n"
    for path in file_paths:
        file_name = os.path.basename(path)
        file_extension = os.path.splitext(file_name)[1].lower()
        file_size = os.path.getsize(path) / 1024  # Convert to KB
        
        file_type = "Unknown"
        if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']:
            file_type = "Medical Image/X-Ray"
            image_count += 1
        elif file_extension == '.pdf':
            file_type = "Medical Report PDF"
            pdf_count += 1
        elif file_extension in ['.doc', '.docx', '.txt', '.rtf']:
            file_type = "Medical Document"
            doc_count += 1
        
        files_info += f"- {file_name} ({file_type}, {file_size:.1f} KB)\n"
    
    # Image-specific guidance for models
    image_guidance = ""
    if image_count > 0:
        image_guidance = """
        IMPORTANT GUIDANCE FOR IMAGE ANALYSIS:
        
        For the medical images provided (X-rays, scans, CBC reports, etc.):
        1. If you see lab reports like CBC, blood tests, metabolic panels:
           - Identify the type of test (CBC, lipid panel, etc.)
           - Look for values outside normal ranges and highlight them
           - Identify patterns like anemia, infection, inflammation based on values
           - Connect abnormal values to patient's symptoms
           
        2. If you see X-rays or radiological images:
           - Describe visible structures and any abnormalities
           - Note any structural issues, opacities, or concerning features
           - Explain how these findings might relate to symptoms
           
        3. For prescription images:
           - Note all medications prescribed
           - Identify dosage and frequency where visible
           - Explain the purpose of these medications
           - Flag any potential interactions with current medications
           
        4. For any medical report images:
           - Look for doctor's notes or summary sections
           - Extract key medical terms, diagnoses, or recommendations
           - Note dates of tests/treatments for timeline context
        """
    
    # Extract text from PDF files if possible
    pdf_text = ""
    try:
        import fitz  # PyMuPDF
        logger.info("PyMuPDF successfully imported, processing PDF files...")
        
        for path in file_paths:
            if path.lower().endswith('.pdf'):
                try:
                    logger.info(f"Processing PDF file: {os.path.basename(path)}")
                    doc = fitz.open(path)
                    page_count = doc.page_count
                    logger.info(f"PDF has {page_count} pages")
                    
                    # Process all pages up to a maximum of 5
                    for page_num in range(min(5, page_count)):
                        try:
                            page = doc[page_num]
                            page_text = page.get_text().strip()
                            text_length = min(1500, len(page_text))  # Increased text length limit further
                            
                            pdf_text += f"\nContent from {os.path.basename(path)} (page {page_num+1}):\n"
                            pdf_text += page_text[:text_length]
                            if text_length < len(page_text):
                                pdf_text += "\n... (truncated)"
                            
                            logger.info(f"Extracted {text_length} characters from page {page_num+1}")
                        except Exception as page_err:
                            logger.error(f"Error extracting text from page {page_num+1}: {str(page_err)}")
                    
                    doc.close()
                except Exception as e:
                    logger.error(f"Failed to extract text from PDF {path}: {str(e)}")
                    logger.error(traceback.format_exc())
    except ImportError:
        logger.warning("PyMuPDF not installed, skipping PDF text extraction")
        pdf_text = "PDF text extraction is not available. Please install PyMuPDF package."
    except Exception as e:
        logger.error(f"Unexpected error during PDF extraction: {str(e)}")
        logger.error(traceback.format_exc())
    
    # Create specialized prompt based on uploaded file types
    file_type_guidance = ""
    if image_count > 0 and pdf_count == 0:
        file_type_guidance = "The user has only uploaded image files. Please provide analysis based on these medical images without text extraction. Look for visual patterns in lab reports, X-rays, or medical documents."
    elif image_count == 0 and pdf_count > 0:
        file_type_guidance = "The user has uploaded PDF documents. Please focus on analyzing the extracted text from these medical reports."
    elif image_count > 0 and pdf_count > 0:
        file_type_guidance = "The user has uploaded both images and PDF documents. Please provide a comprehensive analysis combining information from both types of files."
    
    # Final prompt
    prompt = f"""
    You are a medical assistant tasked with analyzing medical reports, X-rays, and doctor prescriptions.
    
    {patient_profile}
    
    {medical_history_formatted}
    
    {symptoms_text}
    
    {conditions_text}
    
    {recommendations_text}
    
    Uploaded files information:
    {files_info}
    
    {file_type_guidance}
    
    {image_guidance}
    
    {pdf_text if pdf_text else "No text could be extracted from the uploaded files. Please focus on analyzing any medical images provided based on their content type."}
    
    Based on all the provided information, including the patient's profile, symptoms, medical history, and uploaded reports, provide a comprehensive analysis with:

    1. Recommendation: Clear medical recommendations based on reports and symptoms
    2. Follow-up Actions: Specific actions the patient should take 
    3. Risk Factors: Identified risks based on all information
    4. Meal Recommendations: Specific dietary suggestions for breakfast, lunch, dinner
    5. Exercise Plan: Tailored physical activity recommendations
    6. Preventive Measures: Proactive steps to prevent condition deterioration
    7. Do's & Don'ts: Clear lifestyle guidelines
    8. Ayurvedic Medication: Any relevant traditional medicinal approaches
    9. Possible Conditions: Updated assessment of potential conditions with probability percentages
    10. Health Score: A score from 1-10 reflecting overall health status
    11. Key Findings from Reports: Specific insights from the uploaded documents
    12. Summary: A comprehensive overview of the analysis
    
    IMPORTANT GUIDELINES FOR KEY FINDINGS:
    - For lab reports (CBC, blood tests, etc.): Identify abnormal values and their significance
    - For X-rays or scans: Note visible features or abnormalities
    - For reports without extractable text: Use your image analysis capabilities to identify test types, values, and insights
    - Connect findings directly to patient symptoms and conditions
    - For CBC reports specifically: Look for abnormalities in blood cell counts, hemoglobin levels, etc.
    - If you can't extract specific values, note the presence of the test and explain its general purpose in relation to symptoms

    Format the response as JSON with the following structure:
    {{
        "recommendation": "Primary medical advice",
        "followUpActions": ["action1", "action2"],
        "riskFactors": ["risk1", "risk2"],
        "mealRecommendations": {{
            "breakfast": ["meal1", "meal2"],
            "lunch": ["meal1", "meal2"],
            "dinner": ["meal1", "meal2"],
            "note": "Additional dietary guidance"
        }},
        "exercisePlan": ["exercise1", "exercise2"],
        "preventiveMeasures": ["measure1", "measure2"],
        "dos": ["do1", "do2"],
        "donts": ["dont1", "dont2"],
        "ayurvedicMedication": {{
            "recommendations": [
                {{
                    "name": "Medication name",
                    "description": "What it is",
                    "importance": "Why it's recommended",
                    "benefits": "Expected benefits"
                }}
            ]
        }},
        "possibleConditions": [
            {{
                "name": "Condition name",
                "probability": 75,
                "description": "Brief description",
                "category": "respiratory/digestive/neurological/general"
            }}
        ],
        "healthScore": 7,
        "keyFindings": ["finding1", "finding2"],
        "summary": "Comprehensive analysis paragraph"
    }}
    
    Ensure your analysis is medically sound and takes into account both the initial symptoms analysis and the additional information from the uploaded medical documents. If you cannot extract specific values from images, provide general insights based on the type of medical document (CBC report, X-ray, etc.) and how it relates to the patient's symptoms.
    """
    
    logger.info("Created prompt for Gemini API with all patient information and enhanced image/PDF guidance")
    return prompt


# Function to analyze medical reports using Gemini API
def analyze_medical_reports_with_gemini(prompt):
    try:
        if not api_key:
            logger.error("Cannot process request: GEMINI_API_KEY not configured")
            return {"error": "API key not configured"}
        
        genai.configure(api_key=api_key)
        
        # Log that we're about to call the API
        logger.info("Configured Gemini API with API key")
        
        # Create model with more specific parameters
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.3,  # Lower temperature for more deterministic results
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,  # Increased max tokens for more detailed analysis
            },
            safety_settings=safety_settings
        )
        
        logger.info("Sending request to Gemini API...")
        start_time = time.time()
        
        # Add timeout and retry logic
        max_retries = 2
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                response = model.generate_content(prompt, stream=False)
                break  # If successful, break out of the retry loop
            except Exception as e:
                retry_count += 1
                logger.warning(f"Gemini API request failed (attempt {retry_count}/{max_retries}): {str(e)}")
                if retry_count > max_retries:
                    raise  # Re-raise the exception if we've exhausted retries
                time.sleep(2)  # Wait before retrying
        
        elapsed_time = time.time() - start_time
        logger.info(f"Received response from Gemini API in {elapsed_time:.2f} seconds")
        
        try:
            # Check if response contains text
            if not hasattr(response, 'text') or not response.text:
                logger.error("Received empty response from Gemini API")
                return create_fallback_response("The AI model returned an empty response. Please try again.")
            
            response_text = response.text
            logger.info(f"Response text length: {len(response_text)} characters")
            
            # Try to parse as JSON
            try:
                # First, attempt to extract JSON if wrapped in markdown code blocks
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
                if json_match:
                    logger.info("Found JSON in markdown code block")
                    json_str = json_match.group(1)
                    report_analysis = json.loads(json_str)
                else:
                    # Try direct JSON parsing
                    report_analysis = json.loads(response_text)
                
                logger.info("Successfully parsed JSON response")
                
            except json.JSONDecodeError as json_err:
                logger.error(f"Failed to parse JSON response: {str(json_err)}")
                logger.error(f"Response text (first 500 chars): {response_text[:500]}...")
                
                # Try to extract structured data from non-JSON text
                logger.info("Attempting to extract structured data from non-JSON response")
                report_analysis = extract_structured_data_from_text(response_text)
            
            # Add default values for any missing fields
            report_analysis = ensure_complete_response(report_analysis)
            logger.info("Completed response structure with default values where needed")
            
            return report_analysis
            
        except Exception as parsing_err:
            logger.error(f"Error processing Gemini API response: {str(parsing_err)}")
            logger.error(traceback.format_exc())
            return create_fallback_response(f"Error processing AI response: {str(parsing_err)}")
            
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        logger.error(traceback.format_exc())
        return create_fallback_response(f"Error calling AI service: {str(e)}")

# Helper function to create a fallback response
def create_fallback_response(error_message):
    logger.info(f"Creating fallback response with error: {error_message}")
    return {
        "recommendation": f"We encountered an issue analyzing your reports. {error_message} Please consult with a healthcare provider for proper medical advice.",
        "followUpActions": [
            "Consult with a healthcare provider to review your medical reports",
            "Try uploading different report formats (PDF recommended) or clearer images",
            "Consider providing additional context about your symptoms and reports",
            "Schedule a follow-up appointment to discuss your test results in detail"
        ],
        "riskFactors": [
            "Unable to determine specific risk factors from the provided reports",
            "Delayed diagnosis or treatment due to incomplete analysis",
            "Potential oversight of important medical findings"
        ],
        "mealRecommendations": {
            "breakfast": ["Balanced meal with protein, whole grains, and fruits"],
            "lunch": ["Varied diet with vegetables, lean protein, and complex carbohydrates"],
            "dinner": ["Light meal with vegetables, protein, and minimal carbohydrates"],
            "note": "These are general recommendations. Please consult a nutritionist for personalized advice based on your specific test results."
        },
        "exercisePlan": [
            "Regular moderate physical activity appropriate for your condition",
            "Consult with a healthcare provider before starting any exercise regimen",
            "Consider activities that don't exacerbate your symptoms"
        ],
        "preventiveMeasures": [
            "Regular health check-ups with comprehensive blood work",
            "Follow your doctor's advice regarding diagnostic tests",
            "Keep a record of all your symptoms and test results",
            "Maintain a healthy lifestyle with balanced nutrition"
        ],
        "dos": [
            "Maintain a healthy lifestyle with balanced nutrition and regular exercise",
            "Keep all your medical reports organized and accessible",
            "Continue taking prescribed medications as directed by your doctor",
            "Follow up with healthcare providers for proper interpretation of test results"
        ],
        "donts": [
            "Avoid self-medication based on incomplete analysis",
            "Don't ignore persistent symptoms even if analysis was inconclusive",
            "Avoid delaying professional medical consultation",
            "Don't rely solely on automated analysis for medical decisions"
        ],
        "ayurvedicMedication": {"recommendations": []},
        "possibleConditions": [],
        "healthScore": 5,
        "keyFindings": [
            "Your report appears to contain medical data that requires professional interpretation",
            "The system identified the presence of medical reports but couldn't extract specific values",
            "For blood test/CBC reports: These typically measure blood cell counts, hemoglobin levels, and other important markers",
            "For imaging reports: These may contain important structural or functional information relevant to your symptoms",
            "Professional medical review is recommended to fully interpret these results in context with your symptoms"
        ],
        "summary": "We encountered technical difficulties analyzing your specific medical reports. While the system has identified the types of reports you've uploaded, a healthcare professional should review these documents for accurate interpretation. The reports you've provided contain valuable medical information that, when properly analyzed, can help guide your diagnosis and treatment. Please consult with a qualified healthcare provider who can interpret your test results in the context of your medical history and current symptoms."
    }

# Helper function to ensure response has all required fields
def ensure_complete_response(analysis):
    # Define default values for all fields
    defaults = {
        "recommendation": "Please consult with a healthcare provider for a proper medical recommendation.",
        "followUpActions": ["Consult with a healthcare provider"],
        "riskFactors": ["No specific risk factors identified"],
        "mealRecommendations": {
            "breakfast": ["Balanced meal with protein, whole grains, and fruits"],
            "lunch": ["Varied diet with vegetables, lean protein, and complex carbohydrates"],
            "dinner": ["Light meal with vegetables, protein, and minimal carbohydrates"],
            "note": "These are general recommendations. Please consult a nutritionist for personalized advice."
        },
        "exercisePlan": ["Moderate physical activity as appropriate"],
        "preventiveMeasures": ["Regular health check-ups"],
        "dos": ["Maintain a healthy lifestyle"],
        "donts": ["Avoid self-medication"],
        "ayurvedicMedication": {"recommendations": []},
        "possibleConditions": [],
        "healthScore": 5,
        "keyFindings": ["Analysis completed based on provided information"],
        "summary": "The uploaded reports were analyzed in context with your symptoms. Please consult a healthcare provider for accurate interpretation."
    }
    
    # Ensure all keys exist
    for key, default_value in defaults.items():
        if key not in analysis:
            analysis[key] = default_value
        elif analysis[key] is None:
            analysis[key] = default_value
    
    # Handle nested mealRecommendations structure
    if "mealRecommendations" in analysis:
        if not isinstance(analysis["mealRecommendations"], dict):
            analysis["mealRecommendations"] = defaults["mealRecommendations"]
        else:
            for meal_key in ["breakfast", "lunch", "dinner", "note"]:
                if meal_key not in analysis["mealRecommendations"] or not analysis["mealRecommendations"][meal_key]:
                    if meal_key in defaults["mealRecommendations"]:
                        analysis["mealRecommendations"][meal_key] = defaults["mealRecommendations"][meal_key]
    
    # Ensure ayurvedicMedication has correct structure
    if "ayurvedicMedication" in analysis:
        if not isinstance(analysis["ayurvedicMedication"], dict) or "recommendations" not in analysis["ayurvedicMedication"]:
            analysis["ayurvedicMedication"] = {"recommendations": []}
    
    return analysis

# Helper function to extract structured data from non-JSON text
def extract_structured_data_from_text(text):
    # Initialize the result structure
    result = {}
    
    # Try to extract recommendation
    recommendation_match = re.search(r'(?:Recommendation|RECOMMENDATION)[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)', text, re.DOTALL | re.IGNORECASE)
    if recommendation_match:
        result["recommendation"] = recommendation_match.group(1).strip()
    
    # Try to extract health score - look for numbers 1-10
    health_score_match = re.search(r'(?:Health Score|HEALTH SCORE)[:\s]+(\d+(?:\.\d+)?)', text, re.IGNORECASE)
    if health_score_match:
        try:
            score = float(health_score_match.group(1))
            # Ensure score is between 1-10
            score = max(1, min(10, score))
            result["healthScore"] = score
        except ValueError:
            pass
    
    # Try to extract key findings
    findings_section = re.search(r'(?:Key Findings|KEY FINDINGS)(?:from Reports)?[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)', text, re.DOTALL | re.IGNORECASE)
    if findings_section:
        findings_text = findings_section.group(1).strip()
        # Split by bullet points, numbers, or new lines
        findings = re.split(r'(?:\n|•|\*|\d+\.)\s*', findings_text)
        findings = [f.strip() for f in findings if f.strip()]
        if findings:
            result["keyFindings"] = findings
    
    # If no key findings extracted using the pattern above, try broader extraction
    if "keyFindings" not in result or not result["keyFindings"]:
        # Look for CBC or blood test related content
        cbc_section = re.search(r'(?:CBC|Blood Test|Laboratory|Lab Results?|Hematology|Blood Count)[^\n]*(?:\n|.)+?(?=\n\n|\n[A-Z]|$)', text, re.DOTALL | re.IGNORECASE)
        if cbc_section:
            cbc_text = cbc_section.group(0).strip()
            # Extract key points from this section
            lines = [line.strip() for line in cbc_text.split('\n') if line.strip()]
            # Filter out lines that are just headers
            findings = [line for line in lines if len(line) > 10 and not re.match(r'^[A-Z\s]+:$', line)]
            if findings:
                result["keyFindings"] = findings[:5]  # Limit to 5 findings
    
    # If still no findings, check for any mentions of test results
    if "keyFindings" not in result or not result["keyFindings"]:
        test_matches = re.findall(r'(?:indicated|showed|revealed|found|identified|detected|present(?:s|ed)?|observed)[^\n.]+(?:\n|.)+?(?=\n\n|\n[A-Z]|$)', text, re.DOTALL | re.IGNORECASE)
        if test_matches:
            findings = []
            for match in test_matches[:3]:  # Limit to 3 matches
                clean_match = re.sub(r'\s+', ' ', match.strip())
                if len(clean_match) > 10:
                    findings.append(clean_match)
            if findings:
                result["keyFindings"] = findings
    
    # If still no findings, provide a generic finding about the report type
    if "keyFindings" not in result or not result["keyFindings"]:
        # Check if there's any mention of CBC, blood test, or other common tests
        if re.search(r'CBC|blood test|x-ray|MRI|scan|laboratory|hematology', text, re.IGNORECASE):
            result["keyFindings"] = [
                "Medical report identified but specific values could not be extracted",
                "The report appears to contain medical test results relevant to the patient's condition",
                "Further professional interpretation of the medical images is recommended"
            ]
    
    # Try to extract summary
    summary_match = re.search(r'(?:Summary|SUMMARY)[:\s]+(.*?)(?:\n\n|$)', text, re.DOTALL | re.IGNORECASE)
    if summary_match:
        result["summary"] = summary_match.group(1).strip()
    
    # Try to extract follow-up actions
    followup_section = re.search(r'(?:Follow-up Actions?|FOLLOW-UP ACTIONS?)[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)', text, re.DOTALL | re.IGNORECASE)
    if followup_section:
        followup_text = followup_section.group(1).strip()
        # Split by numbers or new lines
        actions = re.split(r'(?:\n|•|\*|\d+\.)\s*', followup_text)
        actions = [a.strip() for a in actions if a.strip()]
        if actions:
            result["followUpActions"] = actions
    
    # Try to extract risk factors
    risk_section = re.search(r'(?:Risk Factors?|RISK FACTORS?)[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)', text, re.DOTALL | re.IGNORECASE)
    if risk_section:
        risk_text = risk_section.group(1).strip()
        # Split by numbers or new lines
        risks = re.split(r'(?:\n|•|\*|\d+\.)\s*', risk_text)
        risks = [r.strip() for r in risks if r.strip()]
        if risks:
            result["riskFactors"] = risks
    
    # Return what we could extract, default values will be added later
    logger.info(f"Extracted {len(result)} fields from non-JSON response")
    return result

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True) 