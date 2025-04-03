import json
import re
import logging
from typing import Dict, List, Any, Union
import os
import traceback
import time

logger = logging.getLogger(__name__)

def setup_logging():
    """Configure logging for the application"""
    # Get the absolute path to the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Configure file handlers with proper paths and encodings
    api_log_path = os.path.join(current_dir, "api.log")
    debug_log_path = os.path.join(current_dir, "debug.log")
    
    # Create handlers
    file_handler = logging.FileHandler(api_log_path, encoding='utf-8')
    debug_file_handler = logging.FileHandler(debug_log_path, encoding='utf-8')
    stream_handler = logging.StreamHandler()
    
    # Set formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Create a more concise formatter for debug logs (single line)
    debug_formatter = logging.Formatter('%(asctime)s - GEMINI_RESPONSE: %(message)s')
    debug_file_handler.setFormatter(debug_formatter)
    
    stream_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
    
    # Configure debug logger (with more detailed logging)
    debug_logger = logging.getLogger('debug')
    debug_logger.setLevel(logging.DEBUG)
    debug_logger.addHandler(debug_file_handler)
    # Ensure debug logger doesn't propagate to root logger
    debug_logger.propagate = False
    
    # Set levels for other loggers to reduce noise
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)

def clean_text(text: str) -> str:
    """Remove asterisks and clean up text formatting"""
    # Remove asterisks
    text = text.replace('*', '')
    # Trim extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_gemini_response(response_text: str) -> Dict:
    """
    Parse the response from Gemini API into a structured format.
    Handles various list formats and ensures comprehensive analysis.
    """
    logging.info("Parsing Gemini response")
    log_debug("Starting to parse Gemini response")
    
    if not response_text:
        log_debug("Empty response received")
        return {
            "possibleConditions": [{
                "name": "Analysis Failed",
                "probability": 100,
                "description": "The analysis could not be completed due to an error.",
                "category": "error"
            }],
            "recommendation": "Please try again or consult a healthcare professional.",
            "urgency": "medium",
            "followUpActions": ["Please try again later"],
            "riskFactors": ["Unable to analyze symptoms"],
            "mealRecommendations": {"breakfast": [], "lunch": [], "dinner": [], "note": ""},
            "exercisePlan": [],
            "diseases": [],
            "preventiveMeasures": [],
            "medicineRecommendations": [],
            "ayurvedicMedication": {
                "description": "",
                "benefits": [],
                "recommendations": [],
                "importance": ""
            },
            "dos": [],
            "donts": [],
            "conditionSpecificData": {},
            "reportsRequired": [],
            "healthScore": 0
        }
    
    # Log the entire Gemini response in a single line format
    response_id = str(int(time.time()))
    log_gemini_response(response_id, response_text)
    
    # Initialize the result dictionary
    result = {
        "possibleConditions": [],
        "recommendation": "",
        "urgency": "medium",
        "followUpActions": [],
        "riskFactors": [],
        "mealRecommendations": {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "note": ""
        },
        "exercisePlan": [],
        "diseases": [],
        "preventiveMeasures": [],
        "medicineRecommendations": [],
        "ayurvedicMedication": {
            "recommendations": []
        },
        "dos": [],
        "donts": [],
        "conditionSpecificData": {},
        "reportsRequired": [],
        "healthScore": 0
    }
    
    try:
        # Split response into sections by heading patterns first
        sections = {}
        section_pattern = r'([A-Z\s\']+):[\r\n]+([\s\S]+?)(?=(?:[A-Z\s\']+:)|$)'
        section_matches = re.finditer(section_pattern, response_text)
        
        for match in section_matches:
            section_name = match.group(1).strip().upper()
            section_content = match.group(2).strip()
            sections[section_name] = section_content
        
        log_debug(f"Extracted {len(sections)} sections from response", {"section_names": list(sections.keys())})
        
        # Try a direct approach to extract conditions
        # First identify the POSSIBLE CONDITIONS section
        possible_conditions_pattern = r'POSSIBLE CONDITIONS:(.*?)(?=RECOMMENDATION:|$)'
        possible_conditions_match = re.search(possible_conditions_pattern, response_text, re.DOTALL | re.IGNORECASE)
        
        if possible_conditions_match:
            conditions_text = possible_conditions_match.group(1).strip()
            logging.info(f"Found conditions section with {len(conditions_text)} characters")
            log_debug("Found conditions section", {"content_length": len(conditions_text), "first_100_chars": conditions_text[:100]})
            
            # Split by numbered conditions (1., 2., 3., etc)
            condition_blocks = re.split(r'\n\s*\d+\.', conditions_text)
            
            # Remove first empty block if present
            if condition_blocks and not condition_blocks[0].strip():
                condition_blocks = condition_blocks[1:]
                
            logging.info(f"Found {len(condition_blocks)} condition blocks")
            log_debug(f"Found {len(condition_blocks)} condition blocks", {"first_block": condition_blocks[0] if condition_blocks else "None"})
            
            # Process each condition block
            for i, block in enumerate(condition_blocks):
                if not block.strip():
                    continue
                
                log_debug(f"Processing condition block {i+1}", {"block_content": block.strip()})
                
                # Extract condition name and probability
                condition_info_pattern = r'([^(]+)\s*\(Probability:\s*(\d+)%\)\s*:?\s*(.*?)(?=\n|$)'
                condition_info_match = re.search(condition_info_pattern, block, re.DOTALL)
                
                if condition_info_match:
                    # Get the full name (might include numbering like "1. Tension Headache")
                    full_name = condition_info_match.group(1).strip()
                    
                    # Remove numbering prefix if present (e.g., "1. " or "2. ")
                    name = re.sub(r'^\d+\.\s*', '', full_name)
                    
                    # Log both the original and cleaned name for debugging
                    log_debug(f"Name extraction: Original '{full_name}' -> Cleaned '{name}'")
                    
                    probability = int(condition_info_match.group(2))
                    description = condition_info_match.group(3).strip()
                    
                    logging.info(f"Extracted condition: {name} ({probability}%)")
                    log_debug(f"Extracted condition details", {
                        "name": name,
                        "probability": probability,
                        "description_length": len(description)
                    })
                    
                    # Add to results
                    result["possibleConditions"].append({
                        "name": name,
                        "probability": probability,
                        "description": description,
                        "category": "general"
                    })
                    
                    # Initialize condition-specific data
                    result["conditionSpecificData"][name] = {
                        "recommendedActions": [],
                        "preventiveMeasures": []
                    }
                    
                    # Extract recommended actions for this condition
                    actions_pattern = r'(?:' + re.escape(name.upper()) + r'|' + re.escape(name) + r')\s*RECOMMENDED\s*ACTIONS:(.*?)(?=' + re.escape(name.upper()) + r'\s*PREVENTIVE|' + re.escape(name) + r'\s*PREVENTIVE|\d+\.\s*\w+\s*\(Probability|RECOMMENDATION:|$)'
                    actions_match = re.search(actions_pattern, response_text, re.DOTALL | re.IGNORECASE)
                    
                    if actions_match:
                        actions_text = actions_match.group(1).strip()
                        log_debug(f"Found actions text for {name}", {"text_length": len(actions_text), "sample": actions_text[:100]})
                        actions = extract_list_items(actions_text)
                        result["conditionSpecificData"][name]["recommendedActions"] = [clean_text(action) for action in actions if action.strip()]
                        logging.info(f"Found {len(result['conditionSpecificData'][name]['recommendedActions'])} recommended actions for {name}")
                        log_debug(f"Extracted actions for {name}", {"actions": result["conditionSpecificData"][name]["recommendedActions"]})
                    else:
                        log_debug(f"No actions found for {name} using pattern", {"pattern": actions_pattern})
                        
                        # Try an alternative pattern if the first one fails
                        alt_actions_pattern = r'(?:' + re.escape(name.upper()) + r'|' + re.escape(name) + r')\s*RECOMMENDED\s*ACTIONS:(.*?)(?=\w+\s*PREVENTIVE\s*MEASURES|RECOMMENDATION:|$)'
                        alt_actions_match = re.search(alt_actions_pattern, response_text, re.DOTALL | re.IGNORECASE)
                        
                        if alt_actions_match:
                            actions_text = alt_actions_match.group(1).strip()
                            log_debug(f"Found actions text using alt pattern for {name}", {"text_length": len(actions_text), "sample": actions_text[:100]})
                            actions = extract_list_items(actions_text)
                            result["conditionSpecificData"][name]["recommendedActions"] = [clean_text(action) for action in actions if action.strip()]
                            logging.info(f"Found {len(result['conditionSpecificData'][name]['recommendedActions'])} recommended actions using alt pattern for {name}")
                            log_debug(f"Extracted actions using alt pattern for {name}", {"actions": result["conditionSpecificData"][name]["recommendedActions"]})
                    
                    # Extract preventive measures for this condition
                    preventive_pattern = r'(?:' + re.escape(name.upper()) + r'|' + re.escape(name) + r')\s*PREVENTIVE\s*MEASURES:(.*?)(?=\d+\.\s*\w+\s*\(Probability|RECOMMENDATION:|$)'
                    preventive_match = re.search(preventive_pattern, response_text, re.IGNORECASE | re.DOTALL)
                    
                    if preventive_match:
                        preventive_text = preventive_match.group(1).strip()
                        log_debug(f"Found preventive measures text for {name}", {"text_length": len(preventive_text), "sample": preventive_text[:100]})
                        preventives = extract_list_items(preventive_text)
                        result["conditionSpecificData"][name]["preventiveMeasures"] = [clean_text(preventive) for preventive in preventives if preventive.strip()]
                        logging.info(f"Found {len(result['conditionSpecificData'][name]['preventiveMeasures'])} preventive measures for {name}")
                        log_debug(f"Extracted preventive measures for {name}", {"measures": result["conditionSpecificData"][name]["preventiveMeasures"]})
                    else:
                        log_debug(f"No preventive measures found for {name} using pattern", {"pattern": preventive_pattern})
                        
                        # Try an alternative pattern if the first one fails
                        alt_preventive_pattern = r'(?:' + re.escape(name.upper()) + r'|' + re.escape(name) + r')\s*PREVENTIVE\s*MEASURES:(.*?)(?=\w+\s*RECOMMENDED\s*ACTIONS|RECOMMENDATION:|$)'
                        alt_preventive_match = re.search(alt_preventive_pattern, response_text, re.IGNORECASE | re.DOTALL)
                        
                        if alt_preventive_match:
                            preventive_text = alt_preventive_match.group(1).strip()
                            log_debug(f"Found preventive measures text using alt pattern for {name}", {"text_length": len(preventive_text), "sample": preventive_text[:100]})
                            preventives = extract_list_items(preventive_text)
                            result["conditionSpecificData"][name]["preventiveMeasures"] = [clean_text(preventive) for preventive in preventives if preventive.strip()]
                            logging.info(f"Found {len(result['conditionSpecificData'][name]['preventiveMeasures'])} preventive measures using alt pattern for {name}")
                            log_debug(f"Extracted preventive measures using alt pattern for {name}", {"measures": result["conditionSpecificData"][name]["preventiveMeasures"]})
                else:
                    log_debug(f"Failed to match condition info for block {i+1}", {"pattern_used": condition_info_pattern})
        
        # If we didn't find conditions the traditional way, fallback to the old approach
        if not result["possibleConditions"]:
            logging.info("Falling back to traditional section parsing")
            log_debug("Fallback to traditional section parsing due to no conditions found")
            
            # Extract possible conditions
            if "POSSIBLE CONDITIONS" in sections:
                conditions_text = sections["POSSIBLE CONDITIONS"]
                log_debug("Processing POSSIBLE CONDITIONS section", {"text_length": len(conditions_text)})
                
                # Extract each condition with numbered list pattern
                condition_pattern = r'(?:^|\n)(?:\d+\.\s*)([^(\r\n]+)(?:\((?:Probability:?\s*)?(\d+)%\))([^:\r\n]*):?(.*?)(?=(?:\n\s*\d+\.)|(?:\n\s*[A-Z][A-Z\s\']*\s*RECOMMENDED\s*ACTIONS)|$)'
                condition_matches = re.findall(condition_pattern, conditions_text, re.DOTALL)
                
                logging.info(f"Found {len(condition_matches)} condition matches")
                log_debug(f"Found {len(condition_matches)} condition matches using fallback pattern")
                
                for match in condition_matches:
                    name = match[0].strip()
                    probability = int(match[1])
                    description = (match[2] + ' ' + match[3]).strip()
                    
                    log_debug(f"Extracted condition using fallback", {"name": name, "probability": probability})
                    
                    result["possibleConditions"].append({
                        "name": name,
                        "probability": probability,
                        "description": description,
                        "category": "general"
                    })
                    
                    # Initialize condition-specific data
                    result["conditionSpecificData"][name] = {
                        "recommendedActions": [],
                        "preventiveMeasures": []
                    }
        
        # If we still haven't found conditions, extract them from individually marked sections
        if not result["possibleConditions"] and sections:
            log_debug("No conditions found through standard patterns, checking for individual condition sections")
            # Look for condition-specific sections
            for section_name, content in sections.items():
                match = re.search(r'(\w+)(?:\s+\w+)*\s+RECOMMENDED\s+ACTIONS', section_name, re.IGNORECASE)
                if match:
                    condition_name = match.group(1).strip()
                    log_debug(f"Found condition section for {condition_name}")
                    
                    # Try to find the corresponding condition in the response
                    condition_pattern = r'(\d+)\.\s*' + re.escape(condition_name) + r'(?:[^\d\n]*)\((?:Probability:?\s*)?(\d+)%\)([^:\n]*)'
                    cond_match = re.search(condition_pattern, response_text, re.IGNORECASE)
                    
                    probability = 0
                    description = ""
                    if cond_match:
                        probability = int(cond_match.group(2))
                        description = cond_match.group(3).strip()
                        log_debug(f"Found probability for {condition_name}", {"probability": probability})
                    
                    # Add the condition
                    if condition_name not in [c["name"] for c in result["possibleConditions"]]:
                        result["possibleConditions"].append({
                            "name": condition_name,
                            "probability": probability,
                            "description": description,
                            "category": "general"
                        })
                        result["conditionSpecificData"][condition_name] = {
                            "recommendedActions": [],
                            "preventiveMeasures": []
                        }
        
        # Ensure all conditions have comprehensive analysis data
        log_debug("Ensuring all conditions have comprehensive analysis data")
        result = ensure_comprehensive_analysis(result)
        
        # Extract general information from sections
        log_debug("Extracting general information from response sections")
        
        # Extract recommendation
        if "RECOMMENDATION" in sections:
            result["recommendation"] = clean_text(sections["RECOMMENDATION"])
            log_debug("Extracted recommendation", {"length": len(result["recommendation"])})
        
        # Extract urgency level
        if "URGENCY LEVEL" in sections:
            urgency_text = sections["URGENCY LEVEL"].lower()
            if 'high' in urgency_text:
                result["urgency"] = "high"
            elif 'medium' in urgency_text or 'moderate' in urgency_text:
                result["urgency"] = "medium"
            else:
                result["urgency"] = "low"
            log_debug("Extracted urgency level", {"urgency": result["urgency"]})
        
        # Extract follow-up actions
        if "FOLLOW-UP ACTIONS" in sections:
            result["followUpActions"] = extract_list_items(sections["FOLLOW-UP ACTIONS"])
            log_debug("Extracted follow-up actions", {"count": len(result["followUpActions"])})
        
        # Extract risk factors
        if "RISK FACTORS" in sections:
            result["riskFactors"] = extract_list_items(sections["RISK FACTORS"])
            log_debug("Extracted risk factors", {"count": len(result["riskFactors"])})
        
        # Extract meal recommendations
        if "INDIAN MEAL RECOMMENDATIONS" in sections:
            meal_text = sections["INDIAN MEAL RECOMMENDATIONS"]
            log_debug("Extracting meal recommendations", {"text_length": len(meal_text)})
            
            # Try to extract breakfast, lunch, and dinner sections
            breakfast_pattern = r'Breakfast:(.*?)(?=Lunch:|$)'
            lunch_pattern = r'Lunch:(.*?)(?=Dinner:|$)'
            dinner_pattern = r'Dinner:(.*?)(?=$)'
            
            breakfast_match = re.search(breakfast_pattern, meal_text, re.DOTALL | re.IGNORECASE)
            lunch_match = re.search(lunch_pattern, meal_text, re.DOTALL | re.IGNORECASE)
            dinner_match = re.search(dinner_pattern, meal_text, re.DOTALL | re.IGNORECASE)
            
            if breakfast_match:
                result["mealRecommendations"]["breakfast"] = extract_list_items(breakfast_match.group(1))
                log_debug("Extracted breakfast meals", {"count": len(result["mealRecommendations"]["breakfast"])})
            
            if lunch_match:
                result["mealRecommendations"]["lunch"] = extract_list_items(lunch_match.group(1))
                log_debug("Extracted lunch meals", {"count": len(result["mealRecommendations"]["lunch"])})
            
            if dinner_match:
                result["mealRecommendations"]["dinner"] = extract_list_items(dinner_match.group(1))
                log_debug("Extracted dinner meals", {"count": len(result["mealRecommendations"]["dinner"])})
            
            # Extract diet note if present
            diet_note_pattern = r'diet preference'
            diet_note_match = re.search(rf'These meal recommendations are based on your.*{diet_note_pattern}.*\.', meal_text, re.IGNORECASE)
            if diet_note_match:
                result["mealRecommendations"]["note"] = diet_note_match.group(0)
                log_debug("Extracted diet note", {"note": result["mealRecommendations"]["note"]})
        
        # Extract exercise plan
        if "EXERCISE PLAN" in sections:
            result["exercisePlan"] = extract_list_items(sections["EXERCISE PLAN"])
            log_debug("Extracted exercise plan", {"count": len(result["exercisePlan"])})
        
        # Extract diseases
        if "POSSIBLE DISEASES" in sections:
            result["diseases"] = extract_list_items(sections["POSSIBLE DISEASES"])
            log_debug("Extracted diseases", {"count": len(result["diseases"])})
        
        # Extract preventive measures
        if "PREVENTIVE MEASURES" in sections:
            result["preventiveMeasures"] = extract_list_items(sections["PREVENTIVE MEASURES"])
            log_debug("Extracted preventive measures", {"count": len(result["preventiveMeasures"])})
        
        # Extract medicine recommendations
        if "MEDICINE RECOMMENDATIONS" in sections:
            result["medicineRecommendations"] = extract_list_items(sections["MEDICINE RECOMMENDATIONS"])
            log_debug("Extracted medicine recommendations", {"count": len(result["medicineRecommendations"])})
        
        # Extract Ayurvedic Medication
        if "AYURVEDIC MEDICATION" in sections:
            ayurvedic_text = sections["AYURVEDIC MEDICATION"]
            log_debug("Extracting Ayurvedic medication", {"text_length": len(ayurvedic_text)})
            
            # Find all Ayurvedic recommendations (numbered items)
            ayurvedic_blocks = re.split(r'\n\s*\d+\.', ayurvedic_text)
            
            # Remove empty first block if present
            if ayurvedic_blocks and not ayurvedic_blocks[0].strip():
                ayurvedic_blocks = ayurvedic_blocks[1:]
                
            log_debug(f"Found {len(ayurvedic_blocks)} Ayurvedic recommendation blocks")
            
            for i, block in enumerate(ayurvedic_blocks):
                if not block.strip():
                    continue
                
                log_debug(f"Processing Ayurvedic recommendation block {i+1}")
                
                # Extract the name (first line of the block)
                name_match = re.match(r'\s*([^\n]+)', block)
                if not name_match:
                    continue
                name = name_match.group(1).strip()
                
                # Extract description
                description = ""
                description_match = re.search(r'- Description:(.*?)(?=- Importance:|$)', block, re.DOTALL)
                if description_match:
                    description = description_match.group(1).strip()
                
                # Extract importance
                importance = ""
                importance_match = re.search(r'- Importance:(.*?)(?=- Benefits:|$)', block, re.DOTALL)
                if importance_match:
                    importance = importance_match.group(1).strip()
                
                # Extract benefits
                benefits = ""
                benefits_match = re.search(r'- Benefits:(.*?)(?=\d+\.|$)', block, re.DOTALL)
                if benefits_match:
                    benefits = benefits_match.group(1).strip()
                
                # Only add if we have at least a name and one of the other fields
                if name and (description or importance or benefits):
                    result["ayurvedicMedication"]["recommendations"].append({
                        "name": name,
                        "description": description,
                        "importance": importance,
                        "benefits": benefits
                    })
                    log_debug(f"Added Ayurvedic recommendation: {name}")
            
            # If we couldn't find any structured recommendations, remove the section
            if not result["ayurvedicMedication"]["recommendations"]:
                result.pop("ayurvedicMedication", None)
                log_debug("No Ayurvedic recommendations found, removing section")
        
        # Extract dos
        if "DO'S" in sections:
            result["dos"] = extract_list_items(sections["DO'S"])
            log_debug("Extracted dos", {"count": len(result["dos"])})
        
        # Extract don'ts
        if "DON'TS" in sections:
            result["donts"] = extract_list_items(sections["DON'TS"])
            log_debug("Extracted don'ts", {"count": len(result["donts"])})
            
        # Extract reports required
        if "REPORTS REQUIRED" in sections:
            reports_text = sections["REPORTS REQUIRED"]
            log_debug("Extracting reports required", {"text_length": len(reports_text)})
            log_debug("Reports section content (sample)", {"sample": reports_text[:300]})
            
            # Extract each report with its detailed information
            result["reportsRequired"] = []
            
            # First identify each report block (starting with numbers)
            report_blocks = re.split(r'\n\s*\d+\.', reports_text)
            
            # Remove empty first item if it exists
            if report_blocks and not report_blocks[0].strip():
                report_blocks = report_blocks[1:]
            
            log_debug(f"Found {len(report_blocks)} report blocks", {"first_block": report_blocks[0][:200] if report_blocks else "None"})
            
            for i, block in enumerate(report_blocks):
                if not block.strip():
                    continue
                    
                log_debug(f"Processing report block {i+1}", {"block_length": len(block), "sample": block[:200]})
                
                # Extract report name (should be the first line)
                name_match = re.match(r'\s*([^\n]+)', block)
                if not name_match:
                    log_debug(f"Failed to extract name for report block {i+1}")
                    continue
                    
                name = name_match.group(1).strip()
                log_debug(f"Extracted report name: {name}")
                
                # Check if the block contains field markers
                has_markers = any(marker in block for marker in ["- Purpose:", "- Benefits:", "- Analysis Details:", "- Preparation Required:", "- Recommendation Reason:"])
                log_debug(f"Block has field markers: {has_markers}")
                
                if not has_markers:
                    log_debug(f"No field markers found in block {i+1} - skipping")
                    continue
                
                # Extract other fields using their markers, preserving multi-line content
                purpose = extract_field_from_block(block, r'- Purpose:\s*')
                benefits = extract_field_from_block(block, r'- Benefits:\s*')
                analysis_details = extract_field_from_block(block, r'- Analysis Details:\s*')
                preparation_required = extract_field_from_block(block, r'- Preparation Required:\s*')
                recommendation_reason = extract_field_from_block(block, r'- Recommendation Reason:\s*')
                
                log_debug(f"Extracted fields for {name}", {
                    "purpose_length": len(purpose),
                    "benefits_length": len(benefits),
                    "analysis_details_length": len(analysis_details),
                    "preparation_required_length": len(preparation_required),
                    "recommendation_reason_length": len(recommendation_reason)
                })
                
                # At least 3 of the 5 fields should have content to consider this a valid report
                field_count = sum(1 for field in [purpose, benefits, analysis_details, preparation_required, recommendation_reason] if field)
                if field_count < 3:
                    log_debug(f"Insufficient fields found for report {name} (only {field_count}/5) - skipping")
                    continue
                
                # Create the report item with preserved multi-line content
                report_item = {
                    "name": f"{name}",
                    "purpose": purpose,
                    "benefits": benefits,
                    "analysisDetails": analysis_details,
                    "preparationRequired": preparation_required,
                    "recommendationReason": recommendation_reason
                }
                
                # Only include fields that have content
                report_item = {k: v for k, v in report_item.items() if v}
                
                # If we've found anything beyond just the name, add it
                if len(report_item) > 1:
                    result["reportsRequired"].append(report_item)
                    log_debug(f"Added report {name} with {len(report_item)} fields")
                else:
                    log_debug(f"Skipped report {name} due to insufficient data")
                
            log_debug("Extracted reports required", {"count": len(result["reportsRequired"])})
            
            # If we didn't find any reports but have the text, do one more attempt to parse them
            if not result["reportsRequired"] and reports_text.strip():
                log_debug("No reports extracted on first pass, trying alternative approach")
                
                # Try looking for each subsection marker directly
                report_name_pattern = r'(?:\d+\.\s*)([^\n\-]+)'
                report_names = re.findall(report_name_pattern, reports_text)
                
                for name in report_names:
                    name = name.strip()
                    log_debug(f"Found report candidate: {name}")
                    
                    # Look for sections after this name
                    name_index = reports_text.find(name)
                    if name_index == -1:
                        continue
                        
                    next_name_index = reports_text.find("\n", name_index + len(name))
                    next_report_index = reports_text.find("\n1.", name_index + len(name))
                    if next_report_index == -1:
                        next_report_index = reports_text.find("\n2.", name_index + len(name))
                    if next_report_index == -1:
                        next_report_index = reports_text.find("\n3.", name_index + len(name))
                    if next_report_index == -1:
                        next_report_index = reports_text.find("\n4.", name_index + len(name))
                    if next_report_index == -1:
                        next_report_index = reports_text.find("\n5.", name_index + len(name))
                    
                    if next_name_index == -1:
                        continue
                        
                    # Extract the block for this report
                    end_index = next_report_index if next_report_index != -1 else len(reports_text)
                    report_block = reports_text[name_index:end_index]
                    
                    # Now extract fields
                    purpose = extract_field_from_block(report_block, r'- Purpose:\s*')
                    benefits = extract_field_from_block(report_block, r'- Benefits:\s*')
                    analysis_details = extract_field_from_block(report_block, r'- Analysis Details:\s*')
                    preparation_required = extract_field_from_block(report_block, r'- Preparation Required:\s*')
                    recommendation_reason = extract_field_from_block(report_block, r'- Recommendation Reason:\s*')
                    
                    report_item = {
                        "name": name,
                        "purpose": purpose,
                        "benefits": benefits,
                        "analysisDetails": analysis_details,
                        "preparationRequired": preparation_required,
                        "recommendationReason": recommendation_reason
                    }
                    
                    # Only include fields that have content
                    report_item = {k: v for k, v in report_item.items() if v}
                    
                    # If we've found anything beyond just the name, add it
                    if len(report_item) > 1:
                        result["reportsRequired"].append(report_item)
                        log_debug(f"Added report {name} with {len(report_item)} fields using alternative method")
                
                log_debug("Completed alternative report extraction", {"count": len(result["reportsRequired"])})
        
        # Extract health score
        if "HEALTH SCORE" in sections:
            health_score_text = sections["HEALTH SCORE"]
            log_debug("Extracting health score", {"text": health_score_text})
            
            # Extract numeric score from format like "7/10 - Explanation"
            score_match = re.search(r'(\d+)/10', health_score_text)
            if score_match:
                result["healthScore"] = int(score_match.group(1))
                log_debug("Extracted health score", {"score": result["healthScore"]})
        
        logging.info(f"Successfully parsed response with {len(result['possibleConditions'])} conditions")
        log_debug("Final parsed result summary", {
            "conditions_count": len(result["possibleConditions"]),
            "urgency": result["urgency"],
            "total_sections_processed": len(sections)
        })
        
        return result
    except Exception as e:
        logging.error(f"Error parsing response: {str(e)}")
        log_debug("Error parsing response", {"error": str(e), "traceback": traceback.format_exc()})
        
        # Initialize with default values in case of error
        return {
            "possibleConditions": [
                {
                    "name": "Error Analyzing Symptoms",
                    "probability": 100,
                    "description": f"There was an error analyzing your symptoms: {str(e)}",
                    "category": "error"
                }
            ],
            "recommendation": "Please try again later or consult a healthcare professional.",
            "urgency": "medium",
            "followUpActions": ["Try again later", "Consult a healthcare professional"],
            "riskFactors": ["Unable to analyze symptoms properly"],
            "mealRecommendations": {"breakfast": [], "lunch": [], "dinner": [], "note": ""},
            "exercisePlan": [],
            "diseases": [],
            "preventiveMeasures": [],
            "medicineRecommendations": [],
            "ayurvedicMedication": {
                "description": "",
                "benefits": [],
                "recommendations": [],
                "importance": ""
            },
            "dos": ["Consult a healthcare professional"],
            "donts": ["Don't rely solely on automated analysis"],
            "conditionSpecificData": {},
            "reportsRequired": [],
            "healthScore": 0
        }

def extract_list_items(text: str) -> List[str]:
    """Extract list items from text, handling various formats"""
    log_debug("Extracting list items from text", {"text_length": len(text), "first_50_chars": text[:50] if text else ""})
    
    if not text or len(text.strip()) == 0:
        log_debug("Empty text provided for list extraction")
        return []
    
    items = []
    
    # Try to extract numbered items (1. Item)
    numbered_regex = r'(?:^|\n)\s*\d+\.\s*([^\n]+)'
    numbered_matches = re.finditer(numbered_regex, text, re.DOTALL)
    numbered_items = [match.group(1).strip() for match in numbered_matches]
    
    if numbered_items:
        log_debug(f"Found {len(numbered_items)} numbered items")
        items = numbered_items
    else:
        # Try to extract dash items (- Item)
        dash_regex = r'(?:^|\n)\s*[\-\*]\s*(.*?)(?=(?:\n\s*[\-\*])|$)'
        dash_matches = re.finditer(dash_regex, text, re.DOTALL)
        dash_items = [match.group(1).strip() for match in dash_matches]
        
        if dash_items:
            log_debug(f"Found {len(dash_items)} dash items")
            items = dash_items
        else:
            # Fallback to splitting by lines and filtering
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # If we have very few lines or lines are very long, use them directly
            if len(lines) < 8 or any(len(line) > 100 for line in lines):
                log_debug(f"Using line splitting fallback - found {len(lines)} lines")
                items = lines
            else:
                # Try to find patterns within the lines
                filtered_lines = []
                for line in lines:
                    # Skip lines that seem like headers
                    if line.isupper() or line.endswith(':'):
                        continue
                    # Skip lines that are just single words
                    words = line.split()
                    if len(words) > 1:
                        filtered_lines.append(line)
                
                if filtered_lines:
                    log_debug(f"Using filtered lines - found {len(filtered_lines)} valid lines")
                    items = filtered_lines
                else:
                    log_debug("No items found using any method")
                    items = []
    
    # Clean items
    cleaned_items = [clean_text(item) for item in items if item.strip()]
    log_debug(f"Extracted and cleaned {len(cleaned_items)} items")
    
    return cleaned_items

def clean_result_text(result: Dict) -> Dict:
    """Ensure all text elements are properly formatted"""
    
    # Clean single string fields
    if "recommendation" in result:
        result["recommendation"] = clean_text(result["recommendation"])
    
    # Clean list fields
    for field in ["followUpActions", "riskFactors", "exercisePlan", "diseases", 
                 "preventiveMeasures", "dos", "donts"]:
        if field in result:
            result[field] = [clean_text(item) for item in result[field]]
    
    # Clean meal recommendations
    if "mealRecommendations" in result:
        for meal_type in ["breakfast", "lunch", "dinner"]:
            if meal_type in result["mealRecommendations"]:
                result["mealRecommendations"][meal_type] = [clean_text(item) for item in result["mealRecommendations"][meal_type]]
        
        if "note" in result["mealRecommendations"]:
            result["mealRecommendations"]["note"] = clean_text(result["mealRecommendations"]["note"])
    
    # Clean condition-specific data
    if "conditionSpecificData" in result:
        for condition in result["conditionSpecificData"]:
            for field in ["recommendedActions", "preventiveMeasures"]:
                if field in result["conditionSpecificData"][condition]:
                    result["conditionSpecificData"][condition][field] = [
                        clean_text(item) for item in result["conditionSpecificData"][condition][field]
                    ]
    
    # Clean reports required
    if "reportsRequired" in result:
        for report in result["reportsRequired"]:
            if "name" in report:
                report["name"] = clean_text(report["name"])
            if "recommendationReason" in report:
                report["recommendationReason"] = clean_text(report["recommendationReason"])
    
    return result

def ensure_comprehensive_analysis(result: Dict) -> Dict:
    """Ensure that the analysis result has all required fields"""
    
    # Provide default values for missing fields
    if "recommendation" not in result or not result["recommendation"]:
        result["recommendation"] = "Please consult a healthcare professional for a thorough diagnosis."
    
    # Ensure urgency is present
    if "urgency" not in result or not result["urgency"]:
        result["urgency"] = "medium"
    
    # Set up default lists for missing list fields
    default_lists = {
        "followUpActions": ["Consult with a healthcare provider", "Monitor your symptoms", "Stay hydrated"],
        "riskFactors": ["Consult a healthcare professional for a full assessment"],
        "exercisePlan": ["Consult your doctor before starting any exercise regimen"],
        "diseases": ["Analysis could not identify specific diseases"],
        "preventiveMeasures": ["Stay hydrated", "Get adequate rest", "Maintain a balanced diet"],
        "dos": ["Seek professional medical advice", "Take notes of your symptoms", "Stay hydrated"],
        "donts": ["Don't self-diagnose", "Don't ignore persistent symptoms", "Don't delay seeking medical help if symptoms worsen"]
    }
    
    for field, default_value in default_lists.items():
        if field not in result or not result[field]:
            result[field] = default_value
    
    # Set up default meal recommendations if missing
    if "mealRecommendations" not in result or not result["mealRecommendations"]:
        result["mealRecommendations"] = {
            "breakfast": ["Consult a nutritionist for personalized meal plans"],
            "lunch": ["Consult a nutritionist for personalized meal plans"],
            "dinner": ["Consult a nutritionist for personalized meal plans"],
            "note": "Consult a healthcare professional for dietary advice."
        }
    else:
        # Ensure all meal types exist
        for meal_type in ["breakfast", "lunch", "dinner"]:
            if meal_type not in result["mealRecommendations"] or not result["mealRecommendations"][meal_type]:
                result["mealRecommendations"][meal_type] = ["Consult a nutritionist for personalized meal plans"]
        
        # Ensure note exists
        if "note" not in result["mealRecommendations"] or not result["mealRecommendations"]["note"]:
            result["mealRecommendations"]["note"] = "Consult a healthcare professional for dietary advice."
    
    # Set default values for new fields if missing
    if "reportsRequired" not in result or not result["reportsRequired"]:
        # Don't add default reports, just keep an empty array
        result["reportsRequired"] = []
    
    if "healthScore" not in result or not result["healthScore"]:
        # Default health score of 5 (average) when no score is provided
        result["healthScore"] = 5
    
    return result

def validate_symptoms(symptoms: List[Dict[str, Any]]) -> Dict[str, Union[bool, str]]:
    """
    Validate that the symptoms are in the correct format and contain required fields.
    Returns a dictionary with 'valid' flag and optional 'message'.
    """
    if not isinstance(symptoms, list):
        return {"valid": False, "message": "Symptoms must be a list"}
    
    if not symptoms:
        return {"valid": False, "message": "At least one symptom is required"}
    
    for i, symptom in enumerate(symptoms):
        if not isinstance(symptom, dict):
            return {"valid": False, "message": f"Symptom at index {i} must be an object"}
        
        # Check required fields
        if 'name' not in symptom:
            return {"valid": False, "message": f"Symptom at index {i} missing 'name' field"}
        
        if not symptom['name']:
            return {"valid": False, "message": f"Symptom at index {i} has empty 'name' field"}
        
        # Check severity is present and valid
        if 'severity' not in symptom:
            return {"valid": False, "message": f"Symptom '{symptom['name']}' missing 'severity' field"}
        
        # Convert severity to string if it's a number
        if isinstance(symptom['severity'], (int, float)):
            symptom['severity'] = str(symptom['severity'])
        
        # Check severity is a valid value (1-10)
        if not isinstance(symptom['severity'], str) or not re.match(r'^(10|[1-9])$', symptom['severity']):
            return {"valid": False, "message": f"Symptom '{symptom['name']}' has invalid severity (must be 1-10)"}
        
        # Check duration is present and valid
        if 'duration' not in symptom:
            return {"valid": False, "message": f"Symptom '{symptom['name']}' missing 'duration' field"}
        
        if not isinstance(symptom['duration'], str) or not symptom['duration']:
            return {"valid": False, "message": f"Symptom '{symptom['name']}' has invalid duration"}
    
    return {"valid": True, "message": "Symptoms validated successfully"}

def log_debug(message, data=None):
    """Log debug messages with optional structured data to debug.log"""
    debug_logger = logging.getLogger('debug')
    
    if data:
        # If data is provided, convert it to a string for logging
        if isinstance(data, (dict, list)):
            import json
            try:
                # Compact JSON format for single-line logging (no indentation)
                data_str = json.dumps(data, separators=(',', ':'), default=str)
                debug_logger.debug(f"{message} - {data_str}")
            except Exception as e:
                debug_logger.debug(f"{message} - Error serializing data: {str(e)}")
        else:
            # Format non-dict/list data on single line
            data_str = str(data).replace('\n', ' ').replace('\r', '')
            debug_logger.debug(f"{message} - {data_str}")
    else:
        debug_logger.debug(message)

def log_gemini_response(response_id, response_text):
    """
    Log Gemini API responses in a single-line format.
    
    Args:
        response_id: A unique identifier for the response (request ID or timestamp)
        response_text: The full text response from Gemini API
    """
    debug_logger = logging.getLogger('debug')
    
    # Clean the response text for single-line logging
    # Replace newlines, tabs, and multiple spaces with single spaces
    clean_text = re.sub(r'\s+', ' ', response_text)
    
    # Truncate if extremely long (keeping beginning and end)
    max_length = 2000
    if len(clean_text) > max_length:
        truncated = clean_text[:max_length//2] + " ... [truncated] ... " + clean_text[-max_length//2:]
        clean_text = truncated
        
    # Log with special prefix for easy filtering
    debug_logger.debug(f"GEMINI_RESPONSE_{response_id}: {clean_text}")

def extract_field_from_block(block, pattern):
    """
    Extract a specific field from a text block using a regex pattern.
    Enhanced to capture multi-line content between section markers and format as numbered list.
    """
    log_debug(f"Extracting field with pattern: {pattern}", {"block_sample": block[:min(len(block), 100)]})
    
    # Try to match the pattern and capture content until another field marker
    field_markers = [
        r'- Purpose:',
        r'- Benefits:',
        r'- Analysis Details:',
        r'- Preparation Required:',
        r'- Recommendation Reason:'
    ]
    
    # Construct a regex that looks for content until the next field marker
    next_field_pattern = '|'.join(map(re.escape, field_markers))
    search_pattern = pattern + r'(.*?)(?=' + next_field_pattern + r'|$)'
    
    # Try to find the match
    try:
        match = re.search(search_pattern, block, re.DOTALL | re.IGNORECASE)
        
        if match:
            content = match.group(1).strip()
            log_debug(f"Found match using main pattern", {"content_length": len(content), "first_50_chars": content[:min(len(content), 50)]})
            
            # Format into numbered list if not already numbered
            if not re.search(r'^\s*\d+\.', content, re.MULTILINE):
                # Split by lines or bullet points
                lines = []
                
                # Check if content contains bullet points
                if "-" in content or "•" in content:
                    # Split by bullet points
                    bullet_pattern = r'(?:^|\n)\s*[-•]\s*(.*?)(?=(?:\n\s*[-•])|$)'
                    bullet_matches = re.finditer(bullet_pattern, content, re.DOTALL)
                    lines = [match.group(1).strip() for match in bullet_matches]
                
                # If no bullet points found, split by lines
                if not lines:
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Format as numbered list
                if lines:
                    numbered_content = ""
                    for i, line in enumerate(lines, 1):
                        numbered_content += f"{i}. {line}\n\n"  # Add double newline for better spacing
                    content = numbered_content.strip()
                    log_debug("Converted content to numbered format with line breaks")
            else:
                # Content is already numbered, ensure each number starts on a new line
                content = re.sub(r'(\d+\..*?)(?=\s*\d+\.|$)', r'\1\n\n', content)
                content = content.strip()
                log_debug("Added line breaks to existing numbered content")
            
            return content
    except Exception as e:
        log_debug(f"Error in main pattern matching: {str(e)}")
    
    # Fallback approach: Look for content until a number followed by a period
    try:
        search_pattern = pattern + r'(.*?)(?=\n\s*\d+\.|$)'
        match = re.search(search_pattern, block, re.DOTALL | re.IGNORECASE)
        
        if match:
            content = match.group(1).strip()
            log_debug(f"Found match using fallback pattern", {"content_length": len(content), "first_50_chars": content[:min(len(content), 50)]})
            
            # Format into numbered list if not already numbered
            if not re.search(r'^\s*\d+\.', content, re.MULTILINE):
                # Split by lines or bullet points
                lines = []
                
                # Check if content contains bullet points
                if "-" in content or "•" in content:
                    # Split by bullet points
                    bullet_pattern = r'(?:^|\n)\s*[-•]\s*(.*?)(?=(?:\n\s*[-•])|$)'
                    bullet_matches = re.finditer(bullet_pattern, content, re.DOTALL)
                    lines = [match.group(1).strip() for match in bullet_matches]
                
                # If no bullet points found, split by lines
                if not lines:
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Format as numbered list
                if lines:
                    numbered_content = ""
                    for i, line in enumerate(lines, 1):
                        numbered_content += f"{i}. {line}\n\n"  # Add double newline for better spacing
                    content = numbered_content.strip()
                    log_debug("Converted content to numbered format with line breaks using fallback approach")
            else:
                # Content is already numbered, ensure each number starts on a new line
                content = re.sub(r'(\d+\..*?)(?=\s*\d+\.|$)', r'\1\n\n', content)
                content = content.strip()
                log_debug("Added line breaks to existing numbered content in fallback approach")
            
            return content
    except Exception as e:
        log_debug(f"Error in fallback pattern matching: {str(e)}")
    
    # Last resort: Just grab anything after the pattern
    try:
        match = re.search(pattern + r'(.*)', block, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1).strip()
            log_debug(f"Found match using last resort pattern", {"content_length": len(content), "first_50_chars": content[:min(len(content), 50)]})
            
            # Format into numbered list if not already numbered
            if not re.search(r'^\s*\d+\.', content, re.MULTILINE):
                # Split by lines
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                
                # Format as numbered list
                if lines:
                    numbered_content = ""
                    for i, line in enumerate(lines, 1):
                        numbered_content += f"{i}. {line}\n\n"  # Add double newline for better spacing
                    content = numbered_content.strip()
                    log_debug("Converted content to numbered format with line breaks using last resort approach")
            else:
                # Content is already numbered, ensure each number starts on a new line
                content = re.sub(r'(\d+\..*?)(?=\s*\d+\.|$)', r'\1\n\n', content)
                content = content.strip()
                log_debug("Added line breaks to existing numbered content in last resort approach")
            
            return content
    except Exception as e:
        log_debug(f"Error in last resort pattern matching: {str(e)}")
    
    log_debug("No match found for pattern")
    return "" 