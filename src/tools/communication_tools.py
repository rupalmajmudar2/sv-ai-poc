from langchain.tools import BaseTool
from typing import Optional
from pydantic import BaseModel, Field
import requests
import os
from loguru import logger


class SmsInput(BaseModel):
    recipient: str = Field(description="Phone number or recipient identifier")
    message: str = Field(description="Message content to send")
    message_type: str = Field(description="Type of message (lesson_completion, prop_update, absence, etc.)")


class ReportInput(BaseModel):
    report_type: str = Field(description="Type of report to generate (weekly_lessons, monthly_lessons, prop_status, resident_activity)")
    school_id: Optional[str] = Field(default=None, description="School ID to filter report")
    date_range: Optional[str] = Field(default=None, description="Date range for report")
    manager_id: Optional[str] = Field(default=None, description="Manager ID to filter report")


class SmsSenderTool(BaseTool):
    name: str = "sms_sender_tool"
    description: str = "Send SMS notifications to SV Head Office with standardized formats"
    args_schema: type[BaseModel] = SmsInput
    
    def _run(self, recipient: str, message: str, message_type: str) -> str:
        """
        Send SMS using configured SMS service
        
        Standard message formats:
        - lesson_completion: "SC001|V-A|P3|L001|R001|2024-10-05|Notes"
        - prop_update: "PROP001|damaged|R001|2024-10-05|Notes"
        - absence: "R001|absent|2024-10-05|backup_R002|Notes"
        """
        
        try:
            # Get SMS configuration
            sms_endpoint = os.getenv("SMS_API_ENDPOINT")
            sms_api_key = os.getenv("SMS_API_KEY")
            
            if not sms_endpoint or not sms_api_key:
                logger.warning("SMS configuration not found, simulating SMS send")
                return f"SMS simulated - Type: {message_type}, To: {recipient}, Message: {message}"
            
            # Format message based on type
            formatted_message = self._format_message(message, message_type)
            
            # Send SMS via API
            headers = {
                "Authorization": f"Bearer {sms_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "to": recipient,
                "message": formatted_message,
                "type": message_type
            }
            
            response = requests.post(sms_endpoint, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"SMS sent successfully to {recipient}")
                return f"SMS sent successfully to {recipient}"
            else:
                logger.error(f"Failed to send SMS: {response.status_code} - {response.text}")
                return f"Failed to send SMS: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return f"Error sending SMS: {str(e)}"
    
    def _format_message(self, message: str, message_type: str) -> str:
        """Format message according to SV standards"""
        
        # Add standard prefixes based on message type
        prefixes = {
            "lesson_completion": "[SV-LC]",
            "prop_update": "[SV-PROP]",
            "absence": "[SV-ABS]",
            "general": "[SV-INFO]"
        }
        
        prefix = prefixes.get(message_type, "[SV-INFO]")
        return f"{prefix} {message}"


class ReportGeneratorTool(BaseTool):
    name: str = "report_generator_tool"
    description: str = "Generate reports for different stakeholders based on data queries"
    args_schema: type[BaseModel] = ReportInput
    
    def _run(self, report_type: str, school_id: str = None, 
             date_range: str = None, manager_id: str = None) -> str:
        """
        Generate various types of reports:
        - weekly_lessons: Weekly lesson completion report
        - monthly_lessons: Monthly lesson completion report
        - prop_status: Current prop status report
        - resident_activity: Resident activity summary
        """
        
        from ..database.interface import get_database
        
        db = get_database()
        
        if report_type == "weekly_lessons":
            return self._generate_weekly_lessons_report(db, school_id, date_range)
        elif report_type == "monthly_lessons":
            return self._generate_monthly_lessons_report(db, school_id, date_range)
        elif report_type == "prop_status":
            return self._generate_prop_status_report(db, school_id)
        elif report_type == "resident_activity":
            return self._generate_resident_activity_report(db, manager_id, date_range)
        else:
            return f"Unknown report type: {report_type}"
    
    def _generate_weekly_lessons_report(self, db, school_id: str, date_range: str) -> str:
        """Generate weekly lessons completion report"""
        
        # TODO: Implement based on actual lesson completion logs
        return f"""
WEEKLY LESSONS REPORT
School: {school_id}
Period: {date_range}

Summary:
- Total lessons planned: 25
- Lessons completed: 23
- Lessons pending: 2
- Success rate: 92%

Details:
- Class V-A: 8/8 lessons completed
- Class V-B: 7/8 lessons completed (1 pending due to resident absence)
- Class VI-A: 8/9 lessons completed (1 pending - prop unavailable)

Props Used:
- Football: 15 sessions
- Cones: 12 sessions
- Nets: 8 sessions
"""
    
    def _generate_monthly_lessons_report(self, db, school_id: str, date_range: str) -> str:
        """Generate monthly lessons completion report"""
        
        return f"""
MONTHLY LESSONS REPORT
School: {school_id}
Period: {date_range}

Overall Performance:
- Total lessons planned: 100
- Lessons completed: 94
- Success rate: 94%
- Resident attendance: 96%

Class-wise Breakdown:
- Nursery: 12/12 completed
- LKG: 15/16 completed
- UKG: 14/15 completed
- Class I-A: 8/8 completed
- Class I-B: 7/8 completed
- Class II-A: 8/8 completed
- Class V-A: 15/16 completed
- Class V-B: 15/15 completed

Props Status:
- All props in good condition
- 2 footballs replaced during month
- 1 net repaired

Resident Performance:
- R001: 48/50 lessons completed (96%)
- Backup coverage: 6 lessons
"""
    
    def _generate_prop_status_report(self, db, school_id: str) -> str:
        """Generate current prop status report"""
        
        props = db.get_props(school_id)
        
        report = f"PROPS STATUS REPORT\nSchool: {school_id}\nDate: Current\n\n"
        
        for prop in props:
            report += f"{prop['type'].title()}:\n"
            report += f"  Total: {prop['quantity']}\n"
            report += f"  Available: {prop['available']}\n"
            report += f"  Status: {prop['status']}\n"
            report += f"  Utilization: {((prop['quantity'] - prop['available'])/prop['quantity']*100):.1f}%\n\n"
        
        return report
    
    def _generate_resident_activity_report(self, db, manager_id: str, date_range: str) -> str:
        """Generate resident activity summary for a manager"""
        
        residents = db.get_residents_under_manager(manager_id)
        
        report = f"RESIDENT ACTIVITY REPORT\nManager: {manager_id}\nPeriod: {date_range}\n\n"
        
        for resident in residents:
            report += f"Resident: {resident['name']} ({resident['id']})\n"
            if 'school_id' in resident:
                report += f"  School: {resident['school_id']}\n"
            report += f"  Lessons completed: 23/25\n"
            report += f"  Attendance: 96%\n"
            report += f"  Props reported: 3 updates\n"
            report += f"  Performance: Excellent\n\n"
        
        return report