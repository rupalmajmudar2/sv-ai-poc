"""
Document Manager for SportzVillage official documentation
Handles indexing and retrieval of SV process documents, SOPs, and guidelines
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..database.vector_store import get_vector_store
from loguru import logger


class SVDocumentManager:
    """Manages SV official documentation for RAG context"""
    
    def __init__(self, docs_directory: str = "data/sv_docs"):
        self.docs_dir = Path(docs_directory)
        self.vector_store = get_vector_store()
        self.document_types = {
            "processes": "Standard Operating Procedures",
            "templates": "Report and Communication Templates", 
            "policies": "Quality Standards and Policies",
            "guidelines": "Best Practices and Guidelines"
        }
    
    def index_sv_documentation(self):
        """Index all SV documentation into vector store"""
        try:
            logger.info("Starting SV documentation indexing...")
            
            for doc_type, description in self.document_types.items():
                type_dir = self.docs_dir / doc_type
                if type_dir.exists():
                    self._index_document_type(doc_type, type_dir, description)
            
            # Index any additional markdown files in root
            for md_file in self.docs_dir.glob("*.md"):
                self._index_single_document(md_file, "general")
            
            logger.info("SV documentation indexing completed")
            
        except Exception as e:
            logger.error(f"Error indexing SV documentation: {e}")
    
    def _index_document_type(self, doc_type: str, type_dir: Path, description: str):
        """Index documents of a specific type"""
        for doc_file in type_dir.glob("*.md"):
            self._index_single_document(doc_file, doc_type)
    
    def _index_single_document(self, doc_path: Path, doc_type: str):
        """Index a single document"""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from filename or first header
            title = doc_path.stem.replace('_', ' ').title()
            
            # Add document metadata
            metadata = {
                "title": title,
                "filename": doc_path.name,
                "doc_type": doc_type,
                "category": "sv_documentation",
                "source": "official_sv_docs"
            }
            
            # Store in vector database
            doc_id = f"sv_doc_{doc_type}_{doc_path.stem}"
            self.vector_store.store_document(doc_id, content, metadata)
            
            logger.info(f"Indexed document: {title}")
            
        except Exception as e:
            logger.error(f"Error indexing {doc_path}: {e}")
    
    def get_relevant_documentation(self, query: str, doc_type: str = None, 
                                 max_docs: int = 3) -> str:
        """Retrieve relevant SV documentation for a query"""
        try:
            # Search in documents collection with SV doc filter
            results = self.vector_store.documents_collection.query(
                query_texts=[query],
                n_results=max_docs,
                where={"category": "sv_documentation"} if not doc_type else {
                    "category": "sv_documentation",
                    "doc_type": doc_type
                }
            )
            
            if not results['documents'] or not results['documents'][0]:
                return ""
            
            # Format results as context
            context_parts = []
            documents = results['documents'][0]
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            
            for i, doc in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}
                title = metadata.get('title', 'Unknown Document')
                doc_type = metadata.get('doc_type', 'general')
                
                context_parts.append(f"""
--- SV Documentation: {title} ({doc_type}) ---
{doc}
""")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error retrieving documentation: {e}")
            return ""
    
    def create_sample_documentation(self):
        """Create sample SV documentation files"""
        os.makedirs(self.docs_dir, exist_ok=True)
        
        # Create sample documents
        sample_docs = {
            "processes/lesson_completion_guide.md": """# Lesson Completion Process - SV Standard

## Overview
All SportzVillage residents must follow this standardized process for logging lesson completion.

## Required Information
1. **School Details**: School ID, Class, Section
2. **Lesson Details**: Lesson ID, Period Number, Date
3. **Resident Information**: Resident ID conducting the lesson
4. **Quality Check**: Verify lesson objectives were met

## Standard Process
1. Complete the lesson as per lesson plan
2. Log completion in SV system within 2 hours
3. Report any prop issues or student absences
4. Send SMS notification to HO using standard format

## SMS Format
`[SV-LC] {school_id}|{class}-{section}|P{period}|{lesson_id}|{resident_id}|{date}|{notes}`

## Quality Standards
- All lessons must align with approved lesson plans
- Prop usage must be tracked accurately
- Any deviations must be documented with reasons
""",
            
            "processes/prop_management_sop.md": """# Props Management - Standard Operating Procedure

## Prop Lifecycle Management
SportzVillage equipment must be managed according to strict protocols.

## Daily Checks
- Verify prop availability before lessons
- Report damaged equipment immediately
- Update prop status in real-time

## Status Categories
- **Good**: Fully functional, safe for use
- **Damaged**: Needs repair, remove from active inventory
- **Missing**: Report to school administration immediately
- **Under Repair**: Temporary status during maintenance

## Reporting Requirements
- Weekly prop inventory reports to School Principal
- Monthly utilization analysis to Regional Manager
- Immediate escalation for safety issues

## Standard Actions
1. **Before Lesson**: Check prop availability and condition
2. **During Lesson**: Monitor for any damage or safety issues
3. **After Lesson**: Return props, update status if needed
4. **Weekly**: Generate comprehensive prop status report
""",
            
            "templates/weekly_report_format.md": """# Weekly Report Template - SV Standard

## Report Structure
All weekly reports to School Principals must follow this format:

### Header
- **School**: {school_name} ({school_id})
- **Week**: {date_range}
- **Prepared by**: {resident_name} ({resident_id})
- **Report Date**: {report_date}

### Lesson Summary
- Total PE periods scheduled: {total_scheduled}
- Lessons completed: {lessons_completed}
- Completion rate: {completion_percentage}%
- Classes covered: {class_list}

### Performance Highlights
- Most active class: {class_section}
- Popular lessons: {lesson_list}
- Student engagement: {engagement_metrics}

### Props Utilization
- Equipment used: {props_summary}
- Condition updates: {condition_changes}
- Maintenance needs: {maintenance_required}

### Challenges & Resolutions
- Issues encountered: {challenges}
- Solutions implemented: {resolutions}
- Support needed: {support_requests}

### Next Week Planning
- Scheduled activities: {planned_activities}
- Special events: {events}
- Resource requirements: {resources_needed}
""",
            
            "policies/quality_standards.md": """# SportzVillage Quality Standards

## Data Accuracy Requirements
- **Zero Tolerance for Inaccurate Reporting**
- All data must be verified before submission
- Cross-validation required for critical metrics

## Response Time Standards
- Lesson completion logging: Within 2 hours
- Prop issue reporting: Immediate (< 30 minutes)
- Weekly reports: Every Friday by 5 PM
- Emergency escalations: Within 15 minutes

## Communication Protocols
- Use only approved SMS formats
- Include all required data fields
- Verify recipient before sending
- Maintain professional tone in all communications

## Escalation Procedures
1. **Level 1**: Resident to Delivery Manager
2. **Level 2**: Delivery Manager to Regional Manager  
3. **Level 3**: Regional Manager to Head Office
4. **Emergency**: Direct to Head Office (safety issues)

## Performance Metrics
- Lesson completion rate: Target 95%+
- Data accuracy: Target 99.5%+
- Report timeliness: Target 100%
- Prop availability: Target 90%+
"""
        }
        
        # Create directory structure and files
        for file_path, content in sample_docs.items():
            full_path = self.docs_dir / file_path
            os.makedirs(full_path.parent, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Created {len(sample_docs)} sample SV documentation files")


# Global document manager instance
_doc_manager = None

def get_sv_document_manager() -> SVDocumentManager:
    """Get global SV document manager instance"""
    global _doc_manager
    
    if _doc_manager is None:
        _doc_manager = SVDocumentManager()
        
        # Create sample docs if they don't exist
        if not _doc_manager.docs_dir.exists():
            _doc_manager.create_sample_documentation()
        
        # Index documentation
        _doc_manager.index_sv_documentation()
    
    return _doc_manager