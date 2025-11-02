"""
OpenAI API helper utilities
"""
import openai
import json
from typing import List, Dict, Optional
import os

class AIHelper:
    """Wrapper for OpenAI API calls"""
    
    def __init__(self, api_key):
        """
        Initialize with API key
        
        Args:
            api_key: OpenAI API key (if None, reads from OPENAI_API_KEY env var)
        """
        self.api_key = api_key 
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        openai.api_key = self.api_key
    
    def extract_topics_from_syllabus(self, syllabus_text: str) -> List[Dict]:
        """
        Extract topics from syllabus text using GPT
        
        Args:
            syllabus_text: Raw syllabus text
            
        Returns:
            List of topic dictionaries with structure:
            [{"name": "Topic Name", "description": "...", "subtopics": [...]}]
        """
        prompt = f"""
You are analyzing a course syllabus. Extract all main topics and their subtopics.

Syllabus:
{syllabus_text}

Return ONLY a valid JSON array (no other text) with this structure:
[
  {{
    "name": "Main Topic Name",
    "description": "Brief description",
    "week": 1,
    "subtopics": ["Subtopic 1", "Subtopic 2"]
  }}
]

Be comprehensive but concise. Identify 5-15 main topics typically.
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured information from educational content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            topics = json.loads(content)
            return topics
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response was: {content}")
            # Return empty list on error
            return []
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return []
    
    def map_question_to_topics(self, question_text: str, topic_names: List[str]) -> Dict:
        """
        Map a quiz question to syllabus topics
        
        Args:
            question_text: The quiz question
            topic_names: List of available topic names
            
        Returns:
            Dictionary with primary_topic and secondary_topics
        """
        topics_str = "\n".join(f"- {topic}" for topic in topic_names)
        
        prompt = f"""
Given this quiz question and list of course topics, identify which topic(s) this question tests.

Question: {question_text}

Available Topics:
{topics_str}

Return ONLY a valid JSON object (no other text) with this structure:
{{
  "primary_topic": "Most relevant topic name",
  "secondary_topics": ["Other relevant topics"],
  "confidence": 0.95
}}

If no clear match, use your best judgment based on keywords and concepts.
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at mapping educational assessment questions to course topics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            mapping = json.loads(content)
            
            return mapping
            
        except Exception as e:
            print(f"Error mapping question to topics: {e}")
            # Return default mapping
            return {
                "primary_topic": topic_names[0] if topic_names else "Unknown",
                "secondary_topics": [],
                "confidence": 0.0
            }
    
    def generate_recommendations(self, 
                                analytics_summary: Dict,
                                syllabus_context: str,
                                quiz_name: str) -> str:
        """
        Generate AI recommendations for instructor
        
        Args:
            analytics_summary: Dictionary with performance analytics
            syllabus_context: Course syllabus text
            quiz_name: Name of the quiz
            
        Returns:
            Formatted recommendations text
        """
        prompt = f"""
You are an educational consultant analyzing quiz results for an instructor.

Quiz: {quiz_name}

Performance Summary:
{json.dumps(analytics_summary, indent=2)}

Course Context:
{syllabus_context[:500]}...

Based on this data, generate 5-7 specific, actionable recommendations to help students improve.

Consider:
1. Which topics need more instructional time
2. Teaching strategies for challenging concepts
3. Differences between class sections (if any)
4. Additional resources or activities
5. Assessment design improvements

Format as a numbered list with brief explanations (2-3 sentences each).
Be specific and practical.
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an experienced educational consultant specializing in data-driven teaching improvements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return "Error generating recommendations. Please try again."