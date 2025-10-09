from langchain.tools import BaseTool
from typing import Optional
from pydantic import BaseModel, Field
from ..database.sv_docs import get_sv_document_manager


class DocumentQueryInput(BaseModel):
    query: str = Field(description="Query to search SV documentation")
    doc_type: Optional[str] = Field(default=None, description="Type of document: processes, templates, policies, guidelines")


class SVDocumentationTool(BaseTool):
    name = "sv_documentation_tool"
    description = "Search SportzVillage official documentation for processes, standards, and guidelines"
    args_schema: type[BaseModel] = DocumentQueryInput
    
    def _run(self, query: str, doc_type: str = None) -> str:
        doc_manager = get_sv_document_manager()
        
        try:
            results = doc_manager.get_relevant_documentation(query, doc_type)
            
            if not results:
                return f"""No specific SV documentation found for '{query}'.

Available documentation categories:
• **Processes**: Standard operating procedures
• **Templates**: Report and communication formats
• **Policies**: Quality standards and requirements
• **Guidelines**: Best practices and recommendations

Try searching for terms like:
- "lesson completion process"
- "prop management standards"  
- "weekly report format"
- "quality requirements"
"""
            
            return f"""**SV Official Documentation Results for '{query}':**

{results}

---
*This information is from official SportzVillage documentation. Please follow these standards and procedures for all activities.*
"""
            
        except Exception as e:
            return f"Error accessing SV documentation: {str(e)}"


class ProcessGuideInput(BaseModel):
    process_name: str = Field(description="Name of the SV process to get guidance for")
    context: Optional[str] = Field(default=None, description="Additional context about the situation")


class SVProcessGuideTool(BaseTool):
    name = "sv_process_guide_tool"
    description = "Get step-by-step guidance for specific SV processes and procedures"
    args_schema: type[BaseModel] = ProcessGuideInput
    
    def _run(self, process_name: str, context: str = None) -> str:
        doc_manager = get_sv_document_manager()
        
        # Map common requests to specific documentation
        process_map = {
            "lesson completion": "lesson completion process standards",
            "prop management": "prop management equipment status",
            "weekly report": "weekly report format template",
            "incident reporting": "escalation procedures incident",
            "sms format": "SMS format communication standards",
            "quality standards": "quality standards data accuracy"
        }
        
        search_query = process_map.get(process_name.lower(), process_name)
        if context:
            search_query += f" {context}"
        
        try:
            results = doc_manager.get_relevant_documentation(search_query)
            
            if not results:
                return f"""No specific process guide found for '{process_name}'.

**Available SV Process Guides:**
• Lesson Completion Process
• Prop Management Standards
• Weekly Report Generation
• Incident Reporting Procedures
• SMS Communication Formats
• Quality Standards Compliance

Please specify one of these processes or provide more details about what you need guidance on.
"""
            
            # Extract actionable steps from documentation
            formatted_guide = f"""**SV Process Guide: {process_name.title()}**

{results}

**Quick Reference:**
• Always follow SV documented procedures
• Verify data accuracy before submission
• Use only approved communication formats
• Escalate issues according to SV protocols
• Maintain records for audit purposes

*Need more specific guidance? Ask about any step in this process.*
"""
            
            return formatted_guide
            
        except Exception as e:
            return f"Error retrieving process guide: {str(e)}"