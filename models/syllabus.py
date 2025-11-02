"""
Data models for syllabus-related entities
"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Topic:
    """Represents a course topic"""
    name: str
    description: Optional[str] = None
    week: Optional[int] = None
    subtopics: List[str] = field(default_factory=list)
    
    def __repr__(self):
        return f"Topic('{self.name}', subtopics={len(self.subtopics)})"
    
    def contains_keyword(self, keyword: str) -> bool:
        """Check if topic name or description contains keyword"""
        keyword_lower = keyword.lower()
        
        if keyword_lower in self.name.lower():
            return True
        
        if self.description and keyword_lower in self.description.lower():
            return True
        
        return any(keyword_lower in sub.lower() for sub in self.subtopics)


class Syllabus:
    """Main syllabus class"""
    
    def __init__(self, course_name: str, course_code: str = ""):
        self.course_name = course_name
        self.course_code = course_code
        self.topics: List[Topic] = []
        self.raw_text: str = ""
    
    def add_topic(self, topic: Topic):
        """Add a topic to the syllabus"""
        self.topics.append(topic)
    
    def get_topic_by_name(self, name: str) -> Optional[Topic]:
        """Find topic by exact name match"""
        return next((t for t in self.topics if t.name.lower() == name.lower()), None)
    
    def search_topics(self, keyword: str) -> List[Topic]:
        """Search for topics containing keyword"""
        return [t for t in self.topics if t.contains_keyword(keyword)]
    
    def get_all_topic_names(self) -> List[str]:
        """Get list of all topic names"""
        return [t.name for t in self.topics]
    
    def __repr__(self):
        return f"Syllabus(course='{self.course_name}', topics={len(self.topics)})"