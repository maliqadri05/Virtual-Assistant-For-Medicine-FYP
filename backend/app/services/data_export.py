"""
Data export service

Handles exporting patient data in various formats (PDF, CSV, JSON, etc.)
"""

import logging
import json
import csv
from typing import Dict, List, Optional, Any
from datetime import datetime
from io import BytesIO, StringIO
from enum import Enum

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats"""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"
    XML = "xml"


class DataExportService:
    """Manages data export in multiple formats"""
    
    def __init__(self):
        """Initialize data export service"""
        logger.info("DataExportService initialized")
    
    def export_patient_data(
        self,
        user_id: str,
        export_data: Dict[str, Any],
        format: str = "json",
        filename: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Export patient data in specified format
        
        Args:
            user_id: User ID
            export_data: Patient data to export
            format: Export format (json, csv, pdf, xml)
            filename: Optional custom filename
        
        Returns:
            Dictionary with export status and file info
        """
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            default_filename = f"patient_data_{user_id}_{timestamp}"
            filename = filename or default_filename
            
            if format == "json":
                return self._export_json(export_data, filename)
            elif format == "csv":
                return self._export_csv(export_data, filename)
            elif format == "pdf":
                return self._export_pdf(export_data, filename)
            elif format == "xml":
                return self._export_xml(export_data, filename)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported export format: {format}"
                }
        
        except Exception as e:
            logger.error(f"Error exporting patient data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_conversation_history(
        self,
        user_id: str,
        conversations: List[Dict],
        format: str = "json"
    ) -> Dict[str, any]:
        """
        Export conversation history
        
        Args:
            user_id: User ID
            conversations: List of conversation objects
            format: Export format
        
        Returns:
            Export result
        """
        try:
            export_data = {
                "export_type": "conversation_history",
                "user_id": user_id,
                "exported_at": datetime.utcnow().isoformat(),
                "total_conversations": len(conversations),
                "conversations": conversations
            }
            
            filename = f"conversations_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}"
            
            return self.export_patient_data(
                user_id,
                export_data,
                format=format,
                filename=filename
            )
        
        except Exception as e:
            logger.error(f"Error exporting conversation history: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_medical_record(
        self,
        user_id: str,
        medical_data: Dict,
        format: str = "pdf"
    ) -> Dict[str, any]:
        """
        Export medical record
        
        Args:
            user_id: User ID
            medical_data: Medical information to export
            format: Export format (default: PDF)
        
        Returns:
            Export result
        """
        try:
            filename = f"medical_record_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}"
            
            return self.export_patient_data(
                user_id,
                medical_data,
                format=format,
                filename=filename
            )
        
        except Exception as e:
            logger.error(f"Error exporting medical record: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _export_json(self, data: Dict, filename: str) -> Dict[str, any]:
        """Export data as JSON"""
        try:
            json_data = json.dumps(data, indent=2, default=str)
            json_bytes = json_data.encode('utf-8')
            
            logger.info(f"Exported data as JSON: {filename}")
            
            return {
                "success": True,
                "format": "json",
                "filename": f"{filename}.json",
                "size_bytes": len(json_bytes),
                "data": json_data
            }
        
        except Exception as e:
            logger.error(f"Error exporting as JSON: {e}")
            return {"success": False, "error": str(e)}
    
    def _export_csv(self, data: Dict, filename: str) -> Dict[str, any]:
        """Export data as CSV"""
        try:
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            if isinstance(data, dict) and "conversations" in data:
                conversations = data["conversations"]
                if conversations:
                    writer.writerow(conversations[0].keys())
                    for conv in conversations:
                        writer.writerow(conv.values())
            else:
                # Generic dict export
                for key, value in data.items():
                    writer.writerow([key, value])
            
            csv_data = output.getvalue()
            csv_bytes = csv_data.encode('utf-8')
            
            logger.info(f"Exported data as CSV: {filename}")
            
            return {
                "success": True,
                "format": "csv",
                "filename": f"{filename}.csv",
                "size_bytes": len(csv_bytes),
                "data": csv_data
            }
        
        except Exception as e:
            logger.error(f"Error exporting as CSV: {e}")
            return {"success": False, "error": str(e)}
    
    def _export_pdf(self, data: Dict, filename: str) -> Dict[str, any]:
        """Export data as PDF (placeholder)"""
        try:
            logger.info(f"Exporting data as PDF: {filename} (placeholder)")
            
            # Placeholder for actual PDF generation
            # In production, integrate with reportlab or weasyprint
            pdf_bytes = b"%PDF-1.4\n[Placeholder PDF Content]"
            
            return {
                "success": True,
                "format": "pdf",
                "filename": f"{filename}.pdf",
                "size_bytes": len(pdf_bytes),
                "message": "PDF export available with reportlab/weasyprint integration"
            }
        
        except Exception as e:
            logger.error(f"Error exporting as PDF: {e}")
            return {"success": False, "error": str(e)}
    
    def _export_xml(self, data: Dict, filename: str) -> Dict[str, any]:
        """Export data as XML (placeholder)"""
        try:
            xml_data = self._dict_to_xml(data)
            xml_bytes = xml_data.encode('utf-8')
            
            logger.info(f"Exported data as XML: {filename}")
            
            return {
                "success": True,
                "format": "xml",
                "filename": f"{filename}.xml",
                "size_bytes": len(xml_bytes),
                "data": xml_data
            }
        
        except Exception as e:
            logger.error(f"Error exporting as XML: {e}")
            return {"success": False, "error": str(e)}
    
    def _dict_to_xml(self, data: Dict, root_name: str = "data") -> str:
        """Convert dictionary to XML string"""
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_lines.append(f"<{root_name}>")
        
        for key, value in data.items():
            if isinstance(value, dict):
                xml_lines.append(f"  <{key}>")
                for k, v in value.items():
                    xml_lines.append(f"    <{k}>{v}</{k}>")
                xml_lines.append(f"  </{key}>")
            elif isinstance(value, list):
                xml_lines.append(f"  <{key}>")
                for item in value:
                    xml_lines.append(f"    <item>{item}</item>")
                xml_lines.append(f"  </{key}>")
            else:
                xml_lines.append(f"  <{key}>{value}</{key}>")
        
        xml_lines.append(f"</{root_name}>")
        return "\n".join(xml_lines)


# Global instance
_export_service = None


def get_data_export_service() -> DataExportService:
    """Get or create global data export service instance"""
    global _export_service
    if _export_service is None:
        _export_service = DataExportService()
    return _export_service
