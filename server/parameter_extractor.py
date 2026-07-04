import os
import json
from typing import Dict, Any, List, Tuple

# Domain Parameter Registry mapping all 11 domains and their exact input schemas.
DOMAIN_SCHEMAS = {
    "student": {
        "name": "Student & Career",
        "question_template": "Is this student/candidate likely to succeed or be eligible for this opportunity?",
        "parameters": {
            "cgpa": {
                "type": "number",
                "required": True,
                "range": [0.0, 10.0],
                "default": 7.5,
                "description": "Current CGPA on a 10-point scale"
            },
            "technical_skills": {
                "type": "chips",
                "required": True,
                "options": {"Beginner": 1, "Intermediate": 2, "Advanced": 3, "Expert": 4},
                "description": "Technical skills proficiency level"
            },
            "internships_done": {
                "type": "chips",
                "required": True,
                "options": {"0": 0, "1": 1, "2": 2, "3+": 3},
                "description": "Number of completed internships"
            },
            "backlogs": {
                "type": "chips",
                "required": True,
                "options": {"No": 0, "Yes": 1},
                "description": "Active backlogs status"
            },
            "study_hours": {
                "type": "chips",
                "required": False,
                "options": {"0 – 2 hrs": 1.0, "2 – 5 hrs": 3.5, "5 – 8 hrs": 6.5, "8+ hrs": 10.0},
                "description": "Average daily study hours"
            },
            "communication_level": {
                "type": "chips",
                "required": False,
                "options": {"Poor": 1, "Average": 2, "Good": 3, "Excellent": 4},
                "description": "Soft skills/communication level"
            }
        }
    },
    "high_school": {
        "name": "High School Outcomes",
        "question_template": "Will this student graduate or drop out?",
        "parameters": {
            "enrollment_age": {
                "type": "chips",
                "required": True,
                "options": {"17 – 19": 18, "20 – 23": 21, "24 – 27": 25, "28 – 35": 31, "36+": 40},
                "description": "Age of enrollment"
            },
            "prev_qualification_grade": {
                "type": "number",
                "required": True,
                "range": [0, 200],
                "default": 130,
                "description": "Previous qualification grade (0-200 scale)"
            },
            "scholarship": {
                "type": "chips",
                "required": True,
                "options": {"Yes": 1, "No": 0},
                "description": "Scholarship holder status"
            },
            "tuition_up_to_date": {
                "type": "chips",
                "required": True,
                "options": {"Yes — fully paid": 1, "No — in arrears": 0},
                "description": "Tuition fees payment status"
            },
            "curricular_units_approved": {
                "type": "chips",
                "required": True,
                "options": {"0": 0, "1 – 3": 2, "4 – 6": 5, "7 – 9": 8, "10+": 11},
                "description": "Approved units in the first semester"
            },
            "displaced": {
                "type": "chips",
                "required": False,
                "options": {"Yes": 1, "No": 0},
                "description": "Displaced person status"
            }
        }
    },
    "job_life": {
        "name": "Job Life Stability",
        "question_template": "Will this professional scenario lead to career stability or a job transition?",
        "parameters": {
            "role_satisfaction": {
                "type": "chips",
                "required": True,
                "options": {"1 – Very Unsatisfied": 1, "2": 2, "3": 3, "4": 4, "5 – Very Satisfied": 5},
                "description": "Role satisfaction rating"
            },
            "lifestyle_balance": {
                "type": "chips",
                "required": True,
                "options": {"1 – Very Poor": 1, "2": 2, "3": 3, "4": 4, "5 – Excellent": 5},
                "description": "Work-life balance rating"
            },
            "tenure_duration": {
                "type": "chips",
                "required": True,
                "options": {"< 1 year": 0.5, "1 – 2 yrs": 1.5, "3 – 5 yrs": 4, "6 – 10 yrs": 8, "10+ yrs": 13},
                "description": "Tenure duration in current position"
            },
            "growth_opportunity": {
                "type": "chips",
                "required": True,
                "options": {"None / Stagnant": 0, "Limited": 1, "Moderate": 2, "Significant": 3, "Exceptional": 4},
                "description": "Growth perception level"
            },
            "workplace_culture": {
                "type": "chips",
                "required": True,
                "options": {"Toxic": 0, "Neutral": 1, "Positive": 2, "Excellent": 3},
                "description": "Workplace culture rating"
            },
            "future_visibility": {
                "type": "chips",
                "required": False,
                "options": {"1 – Completely Unclear": 1, "2": 2, "3": 3, "4": 4, "5 – Highly Defined": 5},
                "description": "Vision clarity rating for future prospects"
            }
        }
    },
    "health": {
        "name": "Health & Wellness",
        "question_template": "What is this person's health risk level?",
        "disclaimer": "This is NOT a medical diagnosis. Always consult a qualified healthcare professional.",
        "parameters": {
            "age": {
                "type": "chips",
                "required": True,
                "options": {"< 30": 25, "30 – 40": 35, "41 – 50": 45, "51 – 60": 55, "61 – 70": 65, "71+": 75},
                "description": "Age range of candidate"
            },
            "glucose": {
                "type": "chips",
                "required": True,
                "options": {"< 70 (Low)": 65, "70 – 99 (Normal)": 85, "100 – 125 (PreDM)": 112, "126 – 199 (High)": 150, "200+ (Very High)": 220},
                "description": "Fasting blood glucose level (mg/dL)"
            },
            "bmi": {
                "type": "chips",
                "required": True,
                "options": {"< 18.5 (Underweight)": 17, "18.5 – 24.9 (Normal)": 22, "25 – 29.9 (Overweight)": 27, "30 – 34.9 (Obese I)": 32, "35+ (Obese II/III)": 38},
                "description": "BMI category"
            },
            "blood_pressure": {
                "type": "chips",
                "required": True,
                "options": {"< 60 (Low)": 55, "60 – 79 (Normal)": 70, "80 – 89 (High)": 85, "90+ (Very High)": 95},
                "description": "Diastolic Blood Pressure (mmHg)"
            },
            "smoking_history": {
                "type": "chips",
                "required": False,
                "options": {"Never": 0, "Former smoker": 1, "Current smoker": 2},
                "description": "Smoking history status"
            },
            "heart_disease": {
                "type": "chips",
                "required": False,
                "options": {"No": 0, "Yes — mild": 1, "Yes — serious": 2},
                "description": "Heart condition/disease status"
            }
        }
    },
    "fitness": {
        "name": "Fitness & Body Performance",
        "question_template": "What is the likelihood of this person being fit/healthy versus having body-related risks?",
        "parameters": {
            "weight_kg": {
                "type": "number",
                "required": True,
                "range": [20, 250],
                "default": 70,
                "description": "Weight in kilograms"
            },
            "height_cm": {
                "type": "number",
                "required": True,
                "range": [100, 250],
                "default": 170,
                "description": "Height in centimeters"
            },
            "age": {
                "type": "chips",
                "required": True,
                "options": {"< 20": 18, "20 – 30": 25, "31 – 40": 35, "41 – 55": 47, "55+": 62},
                "description": "Age group"
            },
            "activity_level": {
                "type": "chips",
                "required": True,
                "options": {"Sedentary": 0, "1–2x/week": 1, "3–4x/week": 2, "Daily": 3},
                "description": "Weekly exercise activity level"
            },
            "body_fat_pct": {
                "type": "chips",
                "required": False,
                "options": {"< 10%": 8, "10 – 18%": 14, "19 – 25%": 22, "26 – 32%": 29, "32%+": 36},
                "description": "Estimated body fat percentage"
            }
        }
    },
    "financial": {
        "name": "Financial Stability",
        "question_template": "Will this financial scenario result in a stable or risky outcome?",
        "disclaimer": "Not a substitute for professional financial or credit assessment.",
        "parameters": {
            "transaction_amount": {
                "type": "chips",
                "required": True,
                "options": {"< ₹1 lakh": 50000, "₹1 – 5 lakh": 250000, "₹5 – 10 lakh": 750000, "₹10 – 25 lakh": 1750000, "₹25 lakh+": 3500000},
                "description": "Transaction amount under evaluation"
            },
            "annual_income": {
                "type": "chips",
                "required": True,
                "options": {"< ₹3 lakh": 200000, "₹3 – 6 lakh": 450000, "₹6 – 12 lakh": 900000, "₹12 – 25 lakh": 1800000, "₹25 lakh+": 3500000},
                "description": "Annual income"
            },
            "stability_duration": {
                "type": "chips",
                "required": True,
                "options": {"Unstable / None": 0, "< 1 year": 0.5, "1 – 3 years": 2, "3 – 7 years": 5, "7 – 15 years": 10, "15+ years": 18},
                "description": "Job/Financial stability duration"
            },
            "financial_score": {
                "type": "chips",
                "required": True,
                "options": {"< 580 (Poor)": 550, "580 – 669 (Fair)": 625, "670 – 739 (Good)": 705, "740 – 799 (Very Good)": 769, "800+ (Exceptional)": 820},
                "description": "Credit score (e.g. CIBIL)"
            },
            "asset_ownership": {
                "type": "chips",
                "required": False,
                "options": {"None / Renting": 0, "Owns primary asset": 1, "Encumbered / Mortgaged": 2, "Diverse portfolio": 3},
                "description": "Asset ownership status"
            },
            "financial_purpose": {
                "type": "chips",
                "required": False,
                "options": {"Personal / Medical": 0, "Education / Growth": 1, "Business / Investment": 2, "Debt Management": 4},
                "description": "Purpose of the financial transaction"
            }
        }
    },
    "mental_health": {
        "name": "Mental Health Evaluation",
        "question_template": "What is this person's mental health risk level?",
        "disclaimer": "Not a psychological diagnosis. Consult a qualified mental health professional. Crisis? Call iCall: 9152987821.",
        "parameters": {
            "sleep_quality": {
                "type": "chips",
                "required": True,
                "options": {"Very poor — < 4 hrs": 0, "Poor — 4 – 5 hrs": 1, "Fair — 5 – 6 hrs": 2, "Good — 6 – 8 hrs": 3, "Excellent — 8+ hrs": 4},
                "description": "Sleep quality rating based on hours"
            },
            "social_support": {
                "type": "chips",
                "required": True,
                "options": {"Isolated — no support": 0, "Weak support": 1, "Moderate support": 2, "Good support": 3, "Strong support network": 4},
                "description": "Support network rating (0 to 4)"
            },
            "work_stress": {
                "type": "chips",
                "required": True,
                "options": {"None": 0, "Low": 1, "Moderate": 2, "High": 3, "Extreme": 4},
                "description": "Job/Work stress rating"
            },
            "physical_activity": {
                "type": "chips",
                "required": True,
                "options": {"None": 0, "Rarely": 1, "Regularly": 2, "Active": 3, "Daily": 4},
                "description": "Physical exercise frequency"
            },
            "anxiety_level": {
                "type": "chips",
                "required": True,
                "options": {"None": 0, "Mild": 1, "Moderate": 2, "Severe": 3, "Very severe": 4},
                "description": "General anxiety rating"
            },
            "age": {
                "type": "chips",
                "required": False,
                "options": {"13 – 17": 15, "18 – 25": 21, "26 – 35": 30, "36 – 50": 43, "51 – 65": 57, "65+": 70},
                "description": "Age group category"
            }
        }
    },
    "claim": {
        "name": "Claim Credibility",
        "question_template": "How credible is this claim?",
        "parameters": {
            "claim_text": {
                "type": "textarea",
                "required": True,
                "description": "Exact statement/claim to analyze"
            },
            "source_type": {
                "type": "chips",
                "required": True,
                "options": {"Social media": 0, "Blog / website": 1, "News outlet": 2, "Government": 3, "Academic paper": 4},
                "description": "Origin platform of claim"
            },
            "source_reliability": {
                "type": "chips",
                "required": True,
                "options": {"1 – Unknown/unreliable": 1, "2": 2, "3": 3, "4": 4, "5 – Highly reliable": 5},
                "description": "Perceived general reliability rating"
            },
            "corroborating_sources": {
                "type": "chips",
                "required": False,
                "options": {"None": 0, "1 – 2": 1, "3 – 5": 4, "5 – 10": 7, "10+": 15},
                "description": "Number of confirming external sources"
            },
            "emotional_language": {
                "type": "chips",
                "required": False,
                "options": {"No — neutral tone": 0, "Somewhat emotional": 1, "Yes — strong emotional push": 2},
                "description": "Apparent emotional tone usage"
            }
        }
    },
    "behavioral": {
        "name": "Behavioral Intent",
        "question_template": "Will this person follow through on their stated intention?",
        "parameters": {
            "commitment_statement": {
                "type": "textarea",
                "required": True,
                "description": "Exact words of intention/commitment"
            },
            "motivation_level": {
                "type": "chips",
                "required": True,
                "options": {"Very low — no conviction": 0, "Low": 1, "Moderate": 2, "High": 3, "Very high — driven to act": 4},
                "description": "Motivation conviction score"
            },
            "past_behavior": {
                "type": "chips",
                "required": True,
                "options": {"Always fails to follow through": 0, "Rarely follows through": 1, "Inconsistent": 2, "Usually follows through": 3, "Always keeps commitments": 4},
                "description": "Past consistency keeping commitments"
            },
            "obstacles_acknowledged": {
                "type": "chips",
                "required": False,
                "options": {"No — pure optimism": 0, "Vaguely mentioned": 1, "Specific obstacles": 2, "Plus solutions": 3},
                "description": "Awareness level of potential obstacles"
            },
            "social_accountability": {
                "type": "chips",
                "required": False,
                "options": {"No one": 0, "Vague mention": 1, "1 – 2 close people": 2, "Public commitment": 3},
                "description": "Social accountability scope"
            },
            "timeline_specificity": {
                "type": "chips",
                "required": False,
                "options": {"Vague — someday": 0, "General — this month": 1, "This week": 2, "Exact date / time": 3},
                "description": "Specificity of the execution timeline"
            }
        }
    },
    "pragma": {
        "name": "PRAGMA (Forensic Psychological Profiling)",
        "question_template": "Analyse this communication for psychological markers and deception.",
        "disclaimer": "PRAGMA is a research-grade forensic psychological profiling tool. Outputs are probabilistic, not definitive verdicts.",
        "parameters": {
            "communication_text": {
                "type": "textarea",
                "required": True,
                "description": "Raw statement, email, transcript, or message"
            },
            "context_type": {
                "type": "chips",
                "required": True,
                "options": {"Personal / social": 0, "Professional / work": 1, "Legal / formal": 2, "Negotiation": 3, "Crisis / high-stakes": 4},
                "description": "Communication context type"
            },
            "stakes_level": {
                "type": "chips",
                "required": True,
                "options": {"Low — casual": 0, "Medium — important": 1, "High — significant": 2, "Critical — very high": 3},
                "description": "Stakes level of outcome"
            },
            "speaker_role": {
                "type": "chips",
                "required": False,
                "options": {"Individual / private": 0, "Employee / staff": 1, "Manager / executive": 2, "Public figure": 3, "Organisation": 4},
                "description": "Role of the speaker"
            },
            "baseline_available": {
                "type": "chips",
                "required": False,
                "options": {"No baseline": 0, "Yes — some examples": 1, "Yes — extensive baseline": 2},
                "description": "Baseline communication samples availability"
            }
        }
    },
    "sarvagna": {
        "name": "Sarvagna (NLP Life Decision Model)",
        "question_template": "Analyse this life decision context for multi-dimensional insights.",
        "parameters": {
            "text_input": {
                "type": "textarea",
                "required": True,
                "description": "Context, news article, or statement"
            },
            "domain_context": {
                "type": "chips",
                "required": True,
                "options": {"News / journalism": 0, "Social media": 1, "Academic / research": 2, "Legal / official": 3, "Medical / health": 4, "General": 5},
                "description": "Domain context"
            },
            "verification_depth": {
                "type": "chips",
                "required": False,
                "options": {"Quick — surface scan": 0, "Standard analysis": 1, "Deep investigation": 2},
                "description": "Analysis/Verification depth level"
            }
        }
    }
}

class DynamicParameterCollector:
    """
    Module design for dynamic domain classification, parameter extraction, and conversational
    missing parameters collection based on a user's initial query.
    """
    
    def __init__(self, schemas: Dict[str, Any] = DOMAIN_SCHEMAS):
        self.schemas = schemas
        
    def classify_domain(self, query: str) -> Tuple[str, float]:
        """
        Classifies the query into one of the 11 registered domains.
        Design: This would typically call a fast LLM (e.g. Groq Llama 3.3) with a system prompt containing the domain descriptions.
        For prototype demonstration, we use a simple heuristic keyword matcher.
        """
        query_lower = query.lower()
        domain_keywords = {
            "student": ["cgpa", "internship", "backlog", "study", "skills", "gpa", "student", "career"],
            "high_school": ["graduation", "qualification", "dropout", "tuition", "arrears", "displaced"],
            "job_life": ["job", "culture", "balance", "lifestyle", "tenure", "growth", "workplace"],
            "health": ["glucose", "blood pressure", "bmi", "medical", "diabetes", "smoker", "smoking", "disease"],
            "fitness": ["weight", "height", "body fat", "fat", "fitness", "activity level"],
            "financial": ["transaction", "income", "credit score", "cibil", "asset", "loan", "financial"],
            "mental_health": ["anxiety", "stress", "sleep", "isolated", "depression", "social support"],
            "claim": ["claim", "corroborate", "reliability", "source", "government", "news", "credible"],
            "behavioral": ["commitment", "intention", "motivation", "obstacle", "accountability", "timeline"],
            "pragma": ["profile", "forensic", "stakes", "negotiation", "deception", "psychological"],
            "sarvagna": ["nlp", "life decision", "journalism", "verification depth", "investigation"]
        }
        
        scores = {domain: 0 for domain in domain_keywords}
        for domain, keywords in domain_keywords.items():
            for kw in keywords:
                if kw in query_lower:
                    scores[domain] += 1
                    
        # Find highest scoring domain
        best_domain = max(scores, key=scores.get)
        if scores[best_domain] > 0:
            return best_domain, float(scores[best_domain])
        
        # Default fallback
        return "student", 0.0

    def extract_existing_parameters(self, query: str, domain: str) -> Dict[str, Any]:
        """
        Extracts parameter values matching the selected domain's schema from the user query.
        Design: This would be implemented via structured JSON extraction using an LLM (e.g. Gemini 1.5 Pro).
        For this prototype, we return a basic rule-based parser or mock dictionary.
        """
        extracted = {}
        schema = self.schemas.get(domain, {}).get("parameters", {})
        
        # Simple extraction example (regex for numbers, option matches for chips)
        for param, config in schema.items():
            param_type = config["type"]
            if param_type == "number":
                # Find any floats/integers in query
                import re
                matches = re.findall(r"\b\d+(?:\.\d+)?\b", query)
                if matches:
                    val = float(matches[0])
                    # Bound checking
                    min_val, max_val = config.get("range", [0, 100])
                    if min_val <= val <= max_val:
                        extracted[param] = val
            elif param_type == "chips":
                # Look for matching option keywords in prompt
                for option_label, option_value in config["options"].items():
                    # Clean/lowercase matching
                    clean_label = option_label.lower().split(" — ")[0].split(" - ")[0]
                    if clean_label in query.lower():
                        extracted[param] = option_value
                        break
            elif param_type == "textarea":
                # Take whole query as statement if requested
                extracted[param] = query
                
        return extracted

    def get_collection_state(self, extracted: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """
        Determines the state of parameter collection by checking which required/optional fields are missing.
        """
        schema = self.schemas.get(domain, {}).get("parameters", {})
        missing_required = []
        missing_optional = []
        
        for param, config in schema.items():
            if param not in extracted:
                if config["required"]:
                    missing_required.append(param)
                else:
                    missing_optional.append(param)
                    
        return {
            "domain": domain,
            "domain_name": self.schemas[domain]["name"],
            "disclaimer": self.schemas[domain].get("disclaimer"),
            "extracted_parameters": extracted,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "is_complete": len(missing_required) == 0
        }

    def generate_parameter_request_ui(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates structured metadata and UI-renderable 'chips' layouts to ask the user
        dynamically for missing parameters.
        """
        if state["is_complete"]:
            return {
                "status": "ready",
                "message": "All required parameters collected. Ready for inference.",
                "ui_elements": []
            }
            
        domain = state["domain"]
        schema = self.schemas[domain]["parameters"]
        next_to_ask = state["missing_required"][0] # Ask one missing required parameter at a time
        param_config = schema[next_to_ask]
        
        # Build dynamic UI prompt
        ui_metadata = {
            "parameter_key": next_to_ask,
            "parameter_type": param_config["type"],
            "description": param_config["description"],
            "prompt_text": f"Please specify your **{param_config['description']}** to proceed."
        }
        
        # Add chip options if it's a chip type
        if param_config["type"] == "chips":
            ui_metadata["chip_options"] = [
                {"label": label, "value": val} for label, val in param_config["options"].items()
            ]
        elif param_config["type"] == "number":
            ui_metadata["input_bounds"] = {
                "min": param_config["range"][0],
                "max": param_config["range"][1],
                "default": param_config["default"]
            }
            
        return {
            "status": "collecting",
            "message": ui_metadata["prompt_text"],
            "ui_elements": ui_metadata
        }

# Example Usage & Verification block
if __name__ == "__main__":
    collector = DynamicParameterCollector()
    
    # Test Scenario: User query missing technical skills and backlogs
    user_query = "I'm a student with 8.5 CGPA and I have completed 2 internships. Will I succeed?"
    print(f"User Query: '{user_query}'")
    
    # 1. Classify domain
    domain, conf = collector.classify_domain(user_query)
    print(f"1. Classified Domain: {domain} (Confidence Score: {conf})")
    
    # 2. Extract parameters already mentioned in query
    extracted = collector.extract_existing_parameters(user_query, domain)
    print(f"2. Extracted Params: {extracted}")
    
    # 3. Check what's missing
    state = collector.get_collection_state(extracted, domain)
    print(f"3. Collection State:")
    print(f"   - Missing Required: {state['missing_required']}")
    print(f"   - Missing Optional: {state['missing_optional']}")
    print(f"   - Is Complete? {state['is_complete']}")
    
    # 4. Generate dynamic UI elements for next missing param
    ui = collector.generate_parameter_request_ui(state)
    print(f"4. Next Question UI Design:\n{json.dumps(ui, indent=2)}")
