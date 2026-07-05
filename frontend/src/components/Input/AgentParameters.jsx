import React, { useState, useEffect } from 'react';
import { Sliders, X, Check, ChevronDown, ChevronUp, RotateCcw } from 'lucide-react';
import './AgentParameters.css';

const AGENT_SCHEMAS = {
  scholar_core: {
    name: 'ScholarCore Academic',
    subdomains: [
      {
        id: 'student',
        label: 'University & Career',
        parameters: {
          cgpa: { type: 'number', label: 'Current CGPA (0-10)', min: 0, max: 10, step: 0.1, default: 7.5 },
          technical_skills: {
            type: 'chips',
            label: 'Technical Proficiency',
            options: { Beginner: 'Beginner', Intermediate: 'Intermediate', Advanced: 'Advanced', Expert: 'Expert' }
          },
          internships_done: {
            type: 'chips',
            label: 'Internships Completed',
            options: { '0': '0', '1': '1', '2': '2', '3+': '3+' }
          },
          backlogs: {
            type: 'chips',
            label: 'Active Backlogs',
            options: { No: 'No', Yes: 'Yes' }
          },
          study_hours: {
            type: 'chips',
            label: 'Daily Study Hours',
            options: { '0-2 hrs': '0-2 hrs', '2-5 hrs': '2-5 hrs', '5-8 hrs': '5-8 hrs', '8+ hrs': '8+ hrs' }
          },
          communication_level: {
            type: 'chips',
            label: 'Soft Skills & Communication',
            options: { Poor: 'Poor', Average: 'Average', Good: 'Good', Excellent: 'Excellent' }
          }
        }
      },
      {
        id: 'high_school',
        label: 'High School Outcomes',
        parameters: {
          enrollment_age: {
            type: 'chips',
            label: 'Enrollment Age',
            options: { '17-19': '17-19', '20-23': '20-23', '24-27': '24-27', '28-35': '28-35', '36+': '36+' }
          },
          prev_qualification_grade: { type: 'number', label: 'Previous Grade (0-200)', min: 0, max: 200, step: 1, default: 130 },
          scholarship: {
            type: 'chips',
            label: 'Scholarship Holder',
            options: { Yes: 'Yes', No: 'No' }
          },
          tuition_up_to_date: {
            type: 'chips',
            label: 'Tuition Payment Status',
            options: { 'Fully Paid': 'Fully Paid', 'In Arrears': 'In Arrears' }
          },
          curricular_units_approved: {
            type: 'chips',
            label: '1st Semester Units Approved',
            options: { '0': '0', '1-3': '1-3', '4-6': '4-6', '7-9': '7-9', '10+': '10+' }
          }
        }
      }
    ]
  },
  career_architect: {
    name: 'CareerArchitect Optimization',
    subdomains: [
      {
        id: 'job_life',
        label: 'Job Life Stability',
        parameters: {
          role_satisfaction: {
            type: 'chips',
            label: 'Role Satisfaction (1-5)',
            options: { '1 - Very Unsatisfied': '1 - Very Unsatisfied', '2': '2', '3': '3', '4': '4', '5 - Very Satisfied': '5 - Very Satisfied' }
          },
          lifestyle_balance: {
            type: 'chips',
            label: 'Work-Life Balance (1-5)',
            options: { '1 - Very Poor': '1 - Very Poor', '2': '2', '3': '3', '4': '4', '5 - Excellent': '5 - Excellent' }
          },
          tenure_duration: {
            type: 'chips',
            label: 'Current Position Tenure',
            options: { '< 1 year': '< 1 year', '1-2 yrs': '1-2 yrs', '3-5 yrs': '3-5 yrs', '6-10 yrs': '6-10 yrs', '10+ yrs': '10+ yrs' }
          },
          growth_opportunity: {
            type: 'chips',
            label: 'Growth Perception',
            options: { 'None / Stagnant': 'None / Stagnant', Limited: 'Limited', Moderate: 'Moderate', Significant: 'Significant', Exceptional: 'Exceptional' }
          },
          workplace_culture: {
            type: 'chips',
            label: 'Workplace Culture',
            options: { Toxic: 'Toxic', Neutral: 'Neutral', Positive: 'Positive', Excellent: 'Excellent' }
          }
        }
      },
      {
        id: 'behavioral',
        label: 'Behavioral Intent & Follow-Through',
        parameters: {
          motivation_level: {
            type: 'chips',
            label: 'Conviction & Motivation',
            options: { 'Very Low': 'Very Low', Low: 'Low', Moderate: 'Moderate', High: 'High', 'Driven to Act': 'Driven to Act' }
          },
          past_behavior: {
            type: 'chips',
            label: 'Past Consistency',
            options: { 'Always Fails': 'Always Fails', 'Rarely Follows': 'Rarely Follows', Inconsistent: 'Inconsistent', 'Usually Follows': 'Usually Follows', 'Always Keeps': 'Always Keeps' }
          },
          obstacles_acknowledged: {
            type: 'chips',
            label: 'Obstacle Awareness',
            options: { 'Pure Optimism': 'Pure Optimism', 'Vaguely Mentioned': 'Vaguely Mentioned', 'Specific Obstacles': 'Specific Obstacles', 'Plus Solutions': 'Plus Solutions' }
          },
          social_accountability: {
            type: 'chips',
            label: 'Accountability Scope',
            options: { 'No One': 'No One', 'Vague Mention': 'Vague Mention', '1-2 Close People': '1-2 Close People', 'Public Commitment': 'Public Commitment' }
          },
          timeline_specificity: {
            type: 'chips',
            label: 'Execution Timeline',
            options: { 'Vague / Someday': 'Vague / Someday', 'This Month': 'This Month', 'This Week': 'This Week', 'Exact Date/Time': 'Exact Date/Time' }
          }
        }
      }
    ]
  },
  fiscal_sentinel: {
    name: 'FiscalSentinel Finance',
    subdomains: [
      {
        id: 'financial',
        label: 'Financial Stability & Allocation',
        parameters: {
          transaction_amount: {
            type: 'chips',
            label: 'Transaction Amount Evaluated',
            options: { '< ₹1 Lakh': '< ₹1 Lakh', '₹1-5 Lakh': '₹1-5 Lakh', '₹5-10 Lakh': '₹5-10 Lakh', '₹10-25 Lakh': '₹10-25 Lakh', '₹25 Lakh+': '₹25 Lakh+' }
          },
          annual_income: {
            type: 'chips',
            label: 'Annual Income Range',
            options: { '< ₹3 Lakh': '< ₹3 Lakh', '₹3-6 Lakh': '₹3-6 Lakh', '₹6-12 Lakh': '₹6-12 Lakh', '₹12-25 Lakh': '₹12-25 Lakh', '₹25 Lakh+': '₹25 Lakh+' }
          },
          stability_duration: {
            type: 'chips',
            label: 'Income Stability Duration',
            options: { 'Unstable / None': 'Unstable / None', '< 1 Year': '< 1 Year', '1-3 Years': '1-3 Years', '3-7 Years': '3-7 Years', '7-15 Years': '7-15 Years', '15+ Years': '15+ Years' }
          },
          financial_score: {
            type: 'chips',
            label: 'Credit Score (CIBIL)',
            options: { '< 580 (Poor)': '< 580 (Poor)', '580-669 (Fair)': '580-669 (Fair)', '670-739 (Good)': '670-739 (Good)', '740-799 (Very Good)': '740-799 (Very Good)', '800+ (Exceptional)': '800+ (Exceptional)' }
          },
          asset_ownership: {
            type: 'chips',
            label: 'Asset Ownership',
            options: { 'None / Renting': 'None / Renting', 'Owns Primary Asset': 'Owns Primary Asset', 'Mortgaged': 'Mortgaged', 'Diverse Portfolio': 'Diverse Portfolio' }
          },
          financial_purpose: {
            type: 'chips',
            label: 'Transaction Purpose',
            options: { 'Personal / Medical': 'Personal / Medical', 'Education / Growth': 'Education / Growth', 'Business / Investment': 'Business / Investment', 'Debt Management': 'Debt Management' }
          }
        }
      }
    ]
  },
  velocity_form: {
    name: 'VelocityForm Fitness',
    subdomains: [
      {
        id: 'fitness',
        label: 'Body Performance & Physiology',
        parameters: {
          weight_kg: { type: 'number', label: 'Weight (kg)', min: 30, max: 200, step: 1, default: 70 },
          height_cm: { type: 'number', label: 'Height (cm)', min: 120, max: 230, step: 1, default: 170 },
          age_group: {
            type: 'chips',
            label: 'Age Group',
            options: { '< 20': '< 20', '20-30': '20-30', '31-40': '31-40', '41-55': '41-55', '55+': '55+' }
          },
          activity_level: {
            type: 'chips',
            label: 'Weekly Activity Frequency',
            options: { Sedentary: 'Sedentary', '1-2x/week': '1-2x/week', '3-4x/week': '3-4x/week', Daily: 'Daily' }
          },
          body_fat_pct: {
            type: 'chips',
            label: 'Estimated Body Fat %',
            options: { '< 10%': '< 10%', '10-18%': '10-18%', '19-25%': '19-25%', '26-32%': '26-32%', '32%+': '32%+' }
          }
        }
      }
    ]
  },
  biometrics_pilot: {
    name: 'BiometricsPilot Preventative Health',
    subdomains: [
      {
        id: 'health',
        label: 'Preventative Health & Vitals',
        parameters: {
          age: {
            type: 'chips',
            label: 'Chronological Age Range',
            options: { '< 30': '< 30', '30-40': '30-40', '41-50': '41-50', '51-60': '51-60', '61-70': '61-70', '71+': '71+' }
          },
          glucose: {
            type: 'chips',
            label: 'Fasting Blood Glucose (mg/dL)',
            options: { '< 70 (Low)': '< 70 (Low)', '70-99 (Normal)': '70-99 (Normal)', '100-125 (PreDM)': '100-125 (PreDM)', '126-199 (High)': '126-199 (High)', '200+ (Very High)': '200+ (Very High)' }
          },
          bmi_category: {
            type: 'chips',
            label: 'BMI Category',
            options: { '< 18.5 (Underweight)': '< 18.5 (Underweight)', '18.5-24.9 (Normal)': '18.5-24.9 (Normal)', '25-29.9 (Overweight)': '25-29.9 (Overweight)', '30-34.9 (Obese I)': '30-34.9 (Obese I)', '35+ (Obese II/III)': '35+ (Obese II/III)' }
          },
          blood_pressure: {
            type: 'chips',
            label: 'Diastolic Blood Pressure (mmHg)',
            options: { '< 60 (Low)': '< 60 (Low)', '60-79 (Normal)': '60-79 (Normal)', '80-89 (High)': '80-89 (High)', '90+ (Very High)': '90+ (Very High)' }
          },
          smoking_history: {
            type: 'chips',
            label: 'Smoking History',
            options: { Never: 'Never', 'Former Smoker': 'Former Smoker', 'Current Smoker': 'Current Smoker' }
          },
          heart_condition: {
            type: 'chips',
            label: 'Heart Condition Status',
            options: { No: 'No', 'Yes - Mild': 'Yes - Mild', 'Yes - Serious': 'Yes - Serious' }
          }
        }
      }
    ]
  },
  zenith_counsel: {
    name: 'ZenithCounsel Cognitive Health',
    subdomains: [
      {
        id: 'mental_health',
        label: 'Cognitive Health & Stress',
        parameters: {
          sleep_quality: {
            type: 'chips',
            label: 'Nightly Sleep Quality',
            options: { 'Very Poor (< 4 hrs)': 'Very Poor (< 4 hrs)', 'Poor (4-5 hrs)': 'Poor (4-5 hrs)', 'Fair (5-6 hrs)': 'Fair (5-6 hrs)', 'Good (6-8 hrs)': 'Good (6-8 hrs)', 'Excellent (8+ hrs)': 'Excellent (8+ hrs)' }
          },
          social_support: {
            type: 'chips',
            label: 'Social Support Network',
            options: { 'Isolated / None': 'Isolated / None', 'Weak Support': 'Weak Support', Moderate: 'Moderate', Good: 'Good', 'Strong Network': 'Strong Network' }
          },
          work_stress: {
            type: 'chips',
            label: 'Current Work/Life Stress Level',
            options: { None: 'None', Low: 'Low', Moderate: 'Moderate', High: 'High', Extreme: 'Extreme' }
          },
          physical_activity: {
            type: 'chips',
            label: 'Exercise Frequency',
            options: { None: 'None', Rarely: 'Rarely', Regularly: 'Regularly', Active: 'Active', Daily: 'Daily' }
          },
          anxiety_level: {
            type: 'chips',
            label: 'General Anxiety Level',
            options: { None: 'None', Mild: 'Mild', Moderate: 'Moderate', Severe: 'Severe', 'Very Severe': 'Very Severe' }
          }
        }
      }
    ]
  },
  nexus_strategist: {
    name: 'NexusStrategist Planning & Logistics',
    subdomains: [
      {
        id: 'pragma',
        label: 'PRAGMA Forensic Profiling',
        parameters: {
          context_type: {
            type: 'chips',
            label: 'Communication Context',
            options: { 'Personal / Social': 'Personal / Social', 'Professional / Work': 'Professional / Work', 'Legal / Formal': 'Legal / Formal', Negotiation: 'Negotiation', 'Crisis / High-Stakes': 'Crisis / High-Stakes' }
          },
          stakes_level: {
            type: 'chips',
            label: 'Stakes Level',
            options: { 'Low (Casual)': 'Low (Casual)', 'Medium (Important)': 'Medium (Important)', 'High (Significant)': 'High (Significant)', 'Critical (Very High)': 'Critical (Very High)' }
          },
          speaker_role: {
            type: 'chips',
            label: 'Speaker Role',
            options: { 'Individual / Private': 'Individual / Private', 'Employee / Staff': 'Employee / Staff', 'Manager / Executive': 'Manager / Executive', 'Public Figure': 'Public Figure', Organisation: 'Organisation' }
          },
          baseline_available: {
            type: 'chips',
            label: 'Baseline Availability',
            options: { 'No Baseline': 'No Baseline', 'Some Examples': 'Some Examples', 'Extensive Baseline': 'Extensive Baseline' }
          }
        }
      },
      {
        id: 'claim',
        label: 'Claim Credibility Analysis',
        parameters: {
          source_type: {
            type: 'chips',
            label: 'Claim Source Origin',
            options: { 'Social Media': 'Social Media', 'Blog / Website': 'Blog / Website', 'News Outlet': 'News Outlet', Government: 'Government', 'Academic Paper': 'Academic Paper' }
          },
          source_reliability: {
            type: 'chips',
            label: 'Source Reliability Rating (1-5)',
            options: { '1 - Unknown/Unreliable': '1 - Unknown/Unreliable', '2': '2', '3': '3', '4': '4', '5 - Highly Reliable': '5 - Highly Reliable' }
          },
          corroborating_sources: {
            type: 'chips',
            label: 'Corroborating Sources Count',
            options: { None: 'None', '1-2': '1-2', '3-5': '3-5', '5-10': '5-10', '10+': '10+' }
          },
          emotional_language: {
            type: 'chips',
            label: 'Emotional Tone',
            options: { 'Neutral Tone': 'Neutral Tone', 'Somewhat Emotional': 'Somewhat Emotional', 'Strong Emotional Push': 'Strong Emotional Push' }
          }
        }
      },
      {
        id: 'sarvagna',
        label: 'Sarvagna NLP Life Decisions',
        parameters: {
          domain_context: {
            type: 'chips',
            label: 'Domain Context',
            options: { 'News / Journalism': 'News / Journalism', 'Social Media': 'Social Media', 'Academic / Research': 'Academic / Research', 'Legal / Official': 'Legal / Official', 'Medical / Health': 'Medical / Health', General: 'General' }
          },
          verification_depth: {
            type: 'chips',
            label: 'Verification Depth Required',
            options: { 'Quick (Surface Scan)': 'Quick (Surface Scan)', 'Standard Analysis': 'Standard Analysis', 'Deep Investigation': 'Deep Investigation' }
          }
        }
      }
    ]
  }
};

const AgentParameters = ({ activeAgent, onParametersChange }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [activeSubdomainIdx, setActiveSubdomainIdx] = useState(0);
  const [selectedParams, setSelectedParams] = useState({});

  const agentId = activeAgent?.id;
  const config = AGENT_SCHEMAS[agentId];

  useEffect(() => {
    // Reset or switch when agent changes
    setActiveSubdomainIdx(0);
    setSelectedParams({});
    setIsExpanded(true);
    if (onParametersChange) onParametersChange({});
  }, [agentId]);

  if (!agentId || !config) return null;

  const currentSubdomain = config.subdomains[activeSubdomainIdx] || config.subdomains[0];
  const parameters = currentSubdomain.parameters;

  const handleChipClick = (paramKey, optionVal) => {
    setSelectedParams(prev => {
      const next = { ...prev };
      if (next[paramKey] === optionVal) {
        delete next[paramKey];
      } else {
        next[paramKey] = optionVal;
      }
      if (onParametersChange) onParametersChange(next);
      return next;
    });
  };

  const handleNumberChange = (paramKey, val) => {
    setSelectedParams(prev => {
      const next = { ...prev, [paramKey]: val };
      if (onParametersChange) onParametersChange(next);
      return next;
    });
  };

  const handleClearAll = (e) => {
    e.stopPropagation();
    setSelectedParams({});
    if (onParametersChange) onParametersChange({});
  };

  const activeCount = Object.keys(selectedParams).length;

  return (
    <div className={`agent-params-drawer ${isExpanded ? 'expanded' : ''}`}>
      {/* Header bar */}
      <div className="agent-params-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="header-left">
          <Sliders size={15} className="params-icon" />
          <span className="params-title">{config.name} Parameters</span>
          {activeCount > 0 ? (
            <span className="params-badge">{activeCount} active</span>
          ) : (
            <span className="params-subtitle">(Click to add context chips)</span>
          )}
        </div>
        <div className="header-right">
          {activeCount > 0 && (
            <button type="button" className="clear-params-btn" onClick={handleClearAll} title="Reset chips">
              <RotateCcw size={13} />
              <span>Reset</span>
            </button>
          )}
          <button type="button" className="toggle-expand-btn">
            {isExpanded ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="agent-params-content">
          {/* Subdomain selector pills if multiple */}
          {config.subdomains.length > 1 && (
            <div className="subdomain-pills">
              {config.subdomains.map((sub, idx) => (
                <button
                  key={sub.id}
                  type="button"
                  className={`subdomain-pill ${idx === activeSubdomainIdx ? 'active' : ''}`}
                  onClick={() => setActiveSubdomainIdx(idx)}
                >
                  {sub.label}
                </button>
              ))}
            </div>
          )}

          {/* Parameter Rows */}
          <div className="params-list">
            {Object.entries(parameters).map(([paramKey, paramCfg]) => (
              <div key={paramKey} className="param-row">
                <span className="param-label">{paramCfg.label}:</span>
                <div className="param-controls">
                  {paramCfg.type === 'chips' && (
                    <div className="chip-options">
                      {Object.entries(paramCfg.options).map(([optLabel, optVal]) => {
                        const isSelected = selectedParams[paramKey] === optVal;
                        return (
                          <button
                            key={optVal}
                            type="button"
                            className={`param-chip ${isSelected ? 'selected' : ''}`}
                            onClick={() => handleChipClick(paramKey, optVal)}
                          >
                            {isSelected && <Check size={12} className="chip-check" />}
                            <span>{optLabel}</span>
                          </button>
                        );
                      })}
                    </div>
                  )}

                  {paramCfg.type === 'number' && (
                    <div className="number-control">
                      <input
                        type="range"
                        min={paramCfg.min}
                        max={paramCfg.max}
                        step={paramCfg.step}
                        value={selectedParams[paramKey] ?? paramCfg.default}
                        onChange={(e) => handleNumberChange(paramKey, parseFloat(e.target.value))}
                        className="param-slider"
                      />
                      <span className="number-val">{selectedParams[paramKey] ?? paramCfg.default}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentParameters;
