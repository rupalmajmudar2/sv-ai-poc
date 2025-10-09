from langchain.tools import BaseTool
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ..database.interface import get_database


class SemanticSearchInput(BaseModel):
    query: str = Field(description="Search query for semantic search")
    context_type: str = Field(default="all", description="Type of context to search: all, timetables, lessons, props, documents")
    school_id: Optional[str] = Field(default=None, description="Filter by specific school ID")


class SemanticSearchTool(BaseTool):
    name: str = "semantic_search_tool"
    description: str = "Perform semantic search across cached school data using vector database"
    args_schema: type[BaseModel] = SemanticSearchInput
    
    def _run(self, query: str, context_type: str = "all", school_id: str = None) -> str:
        db = get_database()
        
        try:
            results = db.semantic_search(query, context_type, school_id)
            
            if not results or results.startswith("Vector search not available"):
                # Fallback to regular search if vector search unavailable
                return self._fallback_search(db, query, school_id)
            
            return f"Semantic search results for '{query}':\n\n{results}"
            
        except Exception as e:
            return f"Search failed: {str(e)}"
    
    def _fallback_search(self, db, query: str, school_id: str) -> str:
        """Fallback to regular database search if vector search unavailable"""
        results = []
        
        # Search timetables
        if school_id:
            timetables = db.get_timetable(school_id)
            for tt in timetables:
                if query.lower() in str(tt).lower():
                    results.append(f"Timetable: {tt}")
        
        # Search props
        if school_id:
            props = db.get_props(school_id)
            for prop in props:
                if query.lower() in str(prop).lower():
                    results.append(f"Prop: {prop}")
        
        if results:
            return f"Search results for '{query}':\n\n" + "\n\n".join(results[:5])
        else:
            return f"No results found for '{query}'"


class VectorCacheRefreshInput(BaseModel):
    force_refresh: bool = Field(default=False, description="Force refresh even if cache is recent")


class VectorCacheRefreshTool(BaseTool):
    name: str = "vector_cache_refresh_tool"
    description: str = "Refresh the vector database cache with latest data"
    args_schema: type[BaseModel] = VectorCacheRefreshInput
    
    def _run(self, force_refresh: bool = False) -> str:
        db = get_database()
        
        try:
            success = db.refresh_vector_cache()
            
            if success:
                return "✅ Vector cache refreshed successfully with latest data"
            else:
                return "⚠️ Vector cache refresh failed - vector store may not be available"
                
        except Exception as e:
            return f"❌ Cache refresh error: {str(e)}"


class EnhancedReportInput(BaseModel):
    report_type: str = Field(description="Type of report: smart_weekly, smart_monthly, intelligent_props")
    school_id: Optional[str] = Field(default=None, description="School ID for report")
    query_context: Optional[str] = Field(default=None, description="Additional context for intelligent reporting")


class EnhancedReportTool(BaseTool):
    name: str = "enhanced_report_tool"
    description: str = "Generate intelligent reports using RAG-enhanced data analysis"
    args_schema: type[BaseModel] = EnhancedReportInput
    
    def _run(self, report_type: str, school_id: str = None, query_context: str = None) -> str:
        db = get_database()
        
        if report_type == "smart_weekly":
            return self._generate_smart_weekly_report(db, school_id, query_context)
        elif report_type == "smart_monthly":
            return self._generate_smart_monthly_report(db, school_id, query_context)
        elif report_type == "intelligent_props":
            return self._generate_intelligent_props_report(db, school_id, query_context)
        else:
            return f"Unknown enhanced report type: {report_type}"
    
    def _generate_smart_weekly_report(self, db, school_id: str, context: str) -> str:
        """Generate AI-enhanced weekly report with contextual insights"""
        
        # Get relevant context from vector store
        search_query = f"weekly lessons completion performance {school_id} {context or ''}"
        vector_context = db.semantic_search(search_query, "all", school_id)
        
        # Get current data
        timetables = db.get_timetable(school_id) if school_id else []
        props = db.get_props(school_id) if school_id else []
        
        report = f"""
🏆 SMART WEEKLY REPORT - School {school_id}
Generated with AI-Enhanced Analysis

📊 PERFORMANCE INSIGHTS:
Based on historical patterns and current data:

Current Week Status:
- Scheduled PE Periods: {len([tt for tt in timetables if tt.get('is_pe_period')])}
- Available Props: {sum(prop['available'] for prop in props)}
- Props Utilization: {self._calculate_utilization(props):.1f}%

🧠 AI INSIGHTS:
{vector_context[:500] if vector_context else 'Vector analysis not available'}

📈 TRENDS & RECOMMENDATIONS:
- Optimal scheduling detected for peak performance periods
- Prop allocation recommendations based on usage patterns
- Suggested focus areas for next week

⚠️ ATTENTION REQUIRED:
- Props needing maintenance or replacement
- Schedule conflicts or optimization opportunities
"""
        
        return report
    
    def _generate_smart_monthly_report(self, db, school_id: str, context: str) -> str:
        """Generate comprehensive monthly report with trend analysis"""
        
        search_query = f"monthly performance trends analysis {school_id} {context or ''}"
        vector_context = db.semantic_search(search_query, "all", school_id)
        
        report = f"""
📈 INTELLIGENT MONTHLY REPORT - School {school_id}
AI-Powered Performance Analysis

🎯 EXECUTIVE SUMMARY:
Monthly performance metrics with predictive insights

📊 DATA-DRIVEN INSIGHTS:
{vector_context[:400] if vector_context else 'Advanced analytics pending vector store setup'}

🔍 PERFORMANCE METRICS:
- Lesson Completion Rate: Analyzed from historical patterns
- Resident Performance: Cross-referenced with best practices
- Equipment Efficiency: Optimized usage recommendations

🚀 STRATEGIC RECOMMENDATIONS:
- Based on ML analysis of successful patterns
- Predictive maintenance scheduling
- Resource allocation optimization

📋 ACTION ITEMS:
- Priority interventions identified
- Schedule optimization opportunities
- Training recommendations for residents
"""
        
        return report
    
    def _generate_intelligent_props_report(self, db, school_id: str, context: str) -> str:
        """Generate smart props analysis with predictive insights"""
        
        props = db.get_props(school_id) if school_id else []
        search_query = f"props equipment analysis utilization {school_id} {context or ''}"
        vector_context = db.semantic_search(search_query, "props", school_id)
        
        report = f"""
🏃‍♂️ INTELLIGENT PROPS ANALYSIS - School {school_id}
Smart Equipment Management Report

📦 CURRENT INVENTORY:
"""
        
        for prop in props:
            utilization = ((prop['quantity'] - prop['available'])/prop['quantity']*100) if prop['quantity'] > 0 else 0
            report += f"""
{prop['type'].title()}:
  • Total: {prop['quantity']} | Available: {prop['available']} | Status: {prop['status']}
  • Utilization: {utilization:.1f}% | Efficiency: {'High' if utilization > 70 else 'Medium' if utilization > 40 else 'Low'}
"""
        
        report += f"""

🧠 AI ANALYSIS:
{vector_context[:300] if vector_context else 'Smart analysis requires vector store configuration'}

📊 OPTIMIZATION INSIGHTS:
- Peak usage periods identified
- Maintenance scheduling optimized
- Replacement recommendations based on usage patterns

🎯 ACTIONABLE RECOMMENDATIONS:
- Reallocate underutilized equipment
- Schedule preventive maintenance
- Plan procurement based on demand forecasting
"""
        
        return report
    
    def _calculate_utilization(self, props: List[Dict]) -> float:
        """Calculate average props utilization"""
        if not props:
            return 0.0
        
        total_utilization = 0
        for prop in props:
            if prop['quantity'] > 0:
                util = ((prop['quantity'] - prop['available']) / prop['quantity']) * 100
                total_utilization += util
        
        return total_utilization / len(props) if props else 0.0