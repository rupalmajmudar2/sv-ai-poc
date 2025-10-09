from langchain.tools import BaseTool
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ..database.interface import get_database
from ..database.sv_docs import get_sv_document_manager


class TimetableQueryInput(BaseModel):
    school_id: str = Field(description="School ID to query timetable for")
    class_name: Optional[str] = Field(default=None, description="Specific class to filter")
    section: Optional[str] = Field(default=None, description="Specific section to filter")


class TimetableTool(BaseTool):
    name: str = "timetable_tool"
    description: str = "Get timetable information for a specific school, class, and section"
    args_schema: type[BaseModel] = TimetableQueryInput
    
    def _run(self, school_id: str, class_name: str = None, section: str = None) -> str:
        db = get_database()
        timetable = db.get_timetable(school_id, class_name, section)
        
        if not timetable:
            return f"No timetable found for school {school_id}"
        
        result = f"Timetable for School {school_id}"
        if class_name:
            result += f", Class {class_name}"
        if section:
            result += f", Section {section}"
        result += ":\n\n"
        
        for entry in timetable:
            result += f"Period {entry['period_number']} ({entry['time_slot']}): {entry['subject']}\n"
        
        return result


class LessonPlanQueryInput(BaseModel):
    school_id: str = Field(description="School ID to query lesson plans for")


class LessonPlanTool(BaseTool):
    name: str = "lesson_plan_tool"
    description: str = "Get lesson plans and lessons for a specific school"
    args_schema: type[BaseModel] = LessonPlanQueryInput
    
    def _run(self, school_id: str) -> str:
        db = get_database()
        lesson_plans = db.get_lesson_plans(school_id)
        
        if not lesson_plans:
            return f"No lesson plans found for school {school_id}"
        
        result = f"Lesson Plans for School {school_id}:\n\n"
        
        for lp in lesson_plans:
            result += f"Lesson Plan {lp['lesson_plan_id']} (Session: {lp['session']}):\n"
            lessons = db.get_lessons(lp['lesson_plan_id'])
            for lesson in lessons:
                result += f"  - {lesson['name']}: {lesson['description']}\n"
                result += f"    Duration: {lesson['duration']} minutes\n"
                result += f"    Required Props: {', '.join(lesson['required_props'])}\n\n"
        
        return result


class PropsQueryInput(BaseModel):
    school_id: str = Field(description="School ID to query props for")


class PropsTool(BaseTool):
    name: str = "props_tool"
    description: str = "Get props inventory and status for a specific school"
    args_schema: type[BaseModel] = PropsQueryInput
    
    def _run(self, school_id: str) -> str:
        db = get_database()
        props = db.get_props(school_id)
        
        if not props:
            return f"No props found for school {school_id}"
        
        result = f"Props Inventory for School {school_id}:\n\n"
        
        for prop in props:
            result += f"{prop['type'].title()}: {prop['available']}/{prop['quantity']} available\n"
            result += f"  Status: {prop['status']}\n"
            result += f"  ID: {prop['prop_id']}\n\n"
        
        return result


class ResidentsQueryInput(BaseModel):
    manager_id: str = Field(description="Manager ID to query residents for")


class ResidentsTool(BaseTool):
    name: str = "residents_tool"
    description: str = "Get list of residents under a specific manager"
    args_schema: type[BaseModel] = ResidentsQueryInput
    
    def _run(self, manager_id: str) -> str:
        db = get_database()
        residents = db.get_residents_under_manager(manager_id)
        
        if not residents:
            return f"No residents found under manager {manager_id}"
        
        result = f"Residents under Manager {manager_id}:\n\n"
        
        for resident in residents:
            result += f"- {resident['name']} (ID: {resident['user_id']})\n"
            if 'school_id' in resident:
                result += f"  Assigned to School: {resident['school_id']}\n"
        
        return result


class LessonCompletionInput(BaseModel):
    school_id: str = Field(description="School ID")
    class_name: str = Field(description="Class name")
    section: str = Field(description="Section")
    period_number: int = Field(description="Period number")
    lesson_id: str = Field(description="Lesson ID completed")
    resident_id: str = Field(description="Resident who conducted the lesson")
    date: str = Field(description="Date of lesson completion (YYYY-MM-DD)")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class LessonCompletionTool(BaseTool):
    name: str = "lesson_completion_tool"
    description: str = "Log completion of a lesson by a resident"
    args_schema: type[BaseModel] = LessonCompletionInput
    
    def _run(self, school_id: str, class_name: str, section: str, 
             period_number: int, lesson_id: str, resident_id: str, 
             date: str, notes: str = None) -> str:
        db = get_database()
        doc_manager = get_sv_document_manager()
        
        # Get SV documentation context for lesson completion
        context = doc_manager.get_relevant_documentation(
            "lesson completion process standards quality requirements",
            doc_type="processes"
        )
        
        data = {
            "school_id": school_id,
            "class": class_name,
            "section": section,
            "period_number": period_number,
            "lesson_id": lesson_id,
            "resident_id": resident_id,
            "date": date,
            "notes": notes
        }
        
        success = db.log_lesson_completion(data)
        
        if success:
            result = f"Successfully logged lesson completion for {class_name}-{section} Period {period_number} by {resident_id}"
            
            # Add SV process context if available
            if context:
                result += "\n\n--- SV Process Compliance ---\n"
                result += "Please ensure the following SV standards are met:\n"
                # Extract key points from documentation
                if "SMS format" in context.lower():
                    result += "• Send SMS notification to HO using standard format\n"
                if "quality" in context.lower():
                    result += "• Verify lesson objectives were achieved\n"
                if "prop" in context.lower():
                    result += "• Update any prop usage or issues\n"
                result += "• Complete logging within 2 hours of lesson completion"
            
            return result
        else:
            return "Failed to log lesson completion"


class PropUpdateInput(BaseModel):
    prop_id: str = Field(description="Prop ID to update")
    status: str = Field(description="New status (good, damaged, missing, etc.)")
    resident_id: str = Field(description="Resident making the update")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class PropUpdateTool(BaseTool):
    name: str = "prop_update_tool"
    description: str = "Update prop status and condition"
    args_schema: type[BaseModel] = PropUpdateInput
    
    def _run(self, prop_id: str, status: str, resident_id: str, notes: str = None) -> str:
        db = get_database()
        doc_manager = get_sv_document_manager()
        
        # Get SV documentation context for prop management
        context = doc_manager.get_relevant_documentation(
            "prop management equipment status reporting standards",
            doc_type="processes"
        )
        
        success = db.update_prop_status(prop_id, status, resident_id)
        
        if success:
            result = f"Successfully updated prop {prop_id} status to {status}"
            
            # Add SV process guidance based on status
            if context:
                result += "\n\n--- SV Prop Management Guidelines ---\n"
                
                if status.lower() == "damaged":
                    result += "• Remove from active inventory immediately\n"
                    result += "• Report to school administration\n"
                    result += "• Schedule repair or replacement"
                elif status.lower() == "missing":
                    result += "• Escalate to school administration immediately\n"
                    result += "• Investigate last known usage\n"
                    result += "• File incident report"
                elif status.lower() == "good":
                    result += "• Return to active inventory\n"
                    result += "• Update utilization metrics"
                
                result += "\n• Update weekly prop report\n"
                result += "• Notify Regional Manager if significant issue"
            
            return result
        else:
            return f"Failed to update prop {prop_id}"