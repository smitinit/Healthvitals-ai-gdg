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
     origins="*", 
     supports_credentials=True, 
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])
setup_logging()

# Setup Google Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logging.error("GOOGLE_API_KEY not found in environment variables")
    print("WARNING: GOOGLE_API_KEY not found in environment variables")
    # Try to manually read from .env file as a fallback
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("GOOGLE_API_KEY="):
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
            logger.error("Cannot process request: GOOGLE_API_KEY not configured")
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
        6. [Optional additional action]
        7. [Optional additional action]
        
        [CONDITION_NAME] PREVENTIVE MEASURES:
        1. [Specific preventive measure for this condition]
        2. [Specific preventive measure for this condition]
        3. [Specific preventive measure for this condition]
        4. [Specific preventive measure for this condition]
        5. [Specific preventive measure for this condition]
        6. [Optional additional preventive measure]
        7. [Optional additional preventive measure]
        
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
        List 5-7 recommended next steps, each on a new line with a number.
        Include specific advice related to the patient's lifestyle factors, medical history (both structured and text-based), allergies, recent life changes and current medications, and symptoms, height, weight, age, gender, where applicable.
        
        RISK FACTORS:
        List 5-7 potential risk factors based on the symptoms and lifestyle factors, and medical history (both structured and text-based), and allergies, and recent life changes and current medications, and symptoms, height, weight, age, gender, each on a new line with a number.
        
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
        List 5-7 preventive measures, especially focusing on improving sleep quality ({sleep_quality}) and managing stress levels ({stress_level}), and diet preference ({diet_preference}), and medical history ({formatted_medical_history}), and lifestyle factors ({exercise_frequency}), and allergies ({allergies}), and recent life changes ({recent_life_changes}) and current medications ({current_medications}), and symptoms ({formatted_symptoms}) with severity and height ({height}), and weight ({weight}), and age ({age}), each on a new line with a number.
        
        MEDICINE RECOMMENDATIONS:
        List 3-5 over-the-counter medicines (with disclaimer to consult doctor), each on a new line with a number.
        Consider any current medications the patient is taking to avoid interactions.
        
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
        Provide a numerical health score from 1-10 (where 10 is perfectly healthy) based on the symptoms, lifestyle factors, and medical history provided (both structured and text-based). Include a brief one-sentence explanation for this score.
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
                    "medicineRecommendations": ["Consult a healthcare professional before taking any medication"],
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
                "medicineRecommendations": ["Consult a healthcare professional before taking any medication"],
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
            logger.error("Cannot process request: GOOGLE_API_KEY not configured")
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 