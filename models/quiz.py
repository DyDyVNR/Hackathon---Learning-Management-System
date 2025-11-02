"""
Data models for quiz-related entities
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Question:
    """Represents a single quiz question"""
    question_id: int
    question_text: str
    correct_answer: str
    points: float
    mapped_topic: Optional[str] = None
    secondary_topics: List[str] = field(default_factory=list)
    
    def __repr__(self):
        return f"Question(id={self.question_id}, topic={self.mapped_topic})"


@dataclass
class StudentResponse:
    """Represents a student's response to a question"""
    question_id: int
    response_text: str
    points_earned: float
    is_correct: bool = False
    
    def get_score_percentage(self, question: Question) -> float:
        """Calculate percentage score for this response"""
        if question.points == 0:
            return 0.0
        return (self.points_earned / question.points) * 100


@dataclass
class Student:
    """Represents a student"""
    student_id: str
    name: str
    section: str  # e.g., "Section A", "Section B", or class 
    responses: List[StudentResponse] = field(default_factory=list)
    
    def get_total_score(self, questions: List[Question]) -> float:
        """Calculate total score across all responses"""
        return sum(r.points_earned for r in self.responses)
    
    def get_total_possible(self, questions: List[Question]) -> float:
        """Calculate total possible points"""
        return sum(q.points for q in questions)
    
    def get_percentage(self, questions: List[Question]) -> float:
        """Calculate overall percentage"""
        total = self.get_total_possible(questions)
        if total == 0:
            return 0.0
        return (self.get_total_score(questions) / total) * 100
    
    def get_weak_topics(self, questions: List[Question], threshold: float = 70.0) -> List[str]:
        """Identify topics where student scored below threshold"""
        weak_topics = []
        
        for response in self.responses:
            question = next((q for q in questions if q.question_id == response.question_id), None)
            if question and question.mapped_topic:
                score_pct = response.get_score_percentage(question)
                if score_pct < threshold:
                    weak_topics.append(question.mapped_topic)
        
        return list(set(weak_topics))  # Remove duplicates


class Quiz:
    """Main quiz class that holds all quiz data"""
    
    def __init__(self, name: str, course_name: str, date: Optional[datetime] = None):
        self.name = name
        self.course_name = course_name
        self.date = date or datetime.now()
        self.questions: List[Question] = []
        self.students: List[Student] = []
    
    def add_question(self, question: Question):
        """Add a question to the quiz"""
        self.questions.append(question)
    
    def add_student(self, student: Student):
        """Add a student to the quiz"""
        self.students.append(student)
    
    def get_question_by_id(self, question_id: int) -> Optional[Question]:
        """Retrieve a question by ID"""
        return next((q for q in self.questions if q.question_id == question_id), None)
    
    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """Retrieve a student by ID"""
        return next((s for s in self.students if s.student_id == student_id), None)
    
    def get_class_average(self) -> float:
        """Calculate overall class average"""
        if not self.students:
            return 0.0
        
        total_percentage = sum(s.get_percentage(self.questions) for s in self.students)
        return total_percentage / len(self.students)
    
    def get_students_by_section(self, section: str) -> List[Student]:
        """Get all students from a specific section"""
        return [s for s in self.students if s.section == section]
    
    def get_section_average(self, section: str) -> float:
        """Calculate average for a specific section"""
        section_students = self.get_students_by_section(section)
        if not section_students:
            return 0.0
        
        total_percentage = sum(s.get_percentage(self.questions) for s in section_students)
        return total_percentage / len(section_students)
    
    def get_all_sections(self) -> List[str]:
        """Get list of all unique sections"""
        return list(set(s.section for s in self.students))
    
    def __repr__(self):
        return f"Quiz(name='{self.name}', questions={len(self.questions)}, students={len(self.students)})"