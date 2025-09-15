"""
Enhanced Configuration Management for BillGenerator OPTIMIZED
Centralized configuration with environment-specific settings
Integrated from BillGeneratorV03's superior configuration system
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile

class EnhancedConfig:
    """
    Advanced configuration management with environment-specific settings
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.load_configuration()
    
    def load_configuration(self):
        """Load comprehensive configuration from environment and defaults"""
        
        # Application Settings
        self.APP_NAME = "Infrastructure Billing System - OPTIMIZED"
        self.APP_VERSION = "2.0.0-ENHANCED"
        self.APP_DESCRIPTION = "Professional Infrastructure Billing Document Generator with Advanced Features"
        
        # File Processing Settings (Enhanced from V03)
        self.MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '100'))  # Increased from 50MB
        self.SUPPORTED_FORMATS = ['xlsx', 'xls']
        self.CHUNK_SIZE = 2000  # Increased for better performance
        
        # PDF Generation Settings (Enhanced)
        self.PDF_PAGE_SIZE = 'A4'
        self.PDF_MARGIN = '10mm'
        self.PDF_ORIENTATION = 'portrait'
        self.PDF_DPI = 300
        self.ENABLE_LATEX_PDF = True  # New feature from V03
        
        # LaTeX Settings (From V03)
        self.LATEX_ENGINE = os.getenv('LATEX_ENGINE', 'pdflatex')
        self.LATEX_TIMEOUT = int(os.getenv('LATEX_TIMEOUT', '60'))
        self.LATEX_ENABLED = self._check_latex_availability()
        
        # Directory Structure (Enhanced)
        self.setup_directories()
        
        # Document Templates (Enhanced from V03)
        self.setup_templates()
        
        # UI Settings (Enhanced)
        self.setup_ui_config()
        
        # Logging Configuration (Enhanced)
        self.setup_logging()
        
        # Processing Settings (Advanced from V03)
        self.setup_processing_config()
        
        # Security Settings
        self.setup_security_config()
        
        # Performance Settings (New)
        self.setup_performance_config()
        
        # Cache Settings (From V03)
        self.setup_cache_config()
    
    def setup_directories(self):
        """Setup enhanced directory structure"""
        self.DIRS = {
            'base': self.base_dir,
            'src': self.base_dir / 'src',
            'templates': self.base_dir / 'templates',
            'latex_templates': self.base_dir / 'LaTeX_Templates',
            'assets': self.base_dir / 'assets',
            'static': self.base_dir / 'static',
            'output': self.base_dir / 'output',
            'temp': Path(tempfile.gettempdir()) / 'billgenerator_enhanced',
            'logs': self.base_dir / 'logs',
            'tests': self.base_dir / 'tests',
            'cache': self.base_dir / 'cache',
            'backup': self.base_dir / 'backup',
            'exports': self.base_dir / 'exports',
            'input_samples': self.base_dir / 'test_input_files'
        }
        
        # Create directories if they don't exist
        for dir_path in self.DIRS.values():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except:
                pass  # Continue if directory creation fails
    
    def setup_templates(self):
        """Setup comprehensive template configuration"""
        self.TEMPLATES = {
            'html': {
                'first_page_summary': 'refer1_first_page.html',
                'deviation_statement': 'refer1_deviation_statement.html',
                'bill_scrutiny': 'final_bill_scrutiny.html',
                'extra_items_statement': 'extra_items_statement.html',
                'certificate_ii': 'certificate_ii.html',
                'certificate_iii': 'certificate_iii.html',
                'note_sheet': 'note_sheet.html'
            },
            'latex': {
                'first_page_summary': 'first_page_summary.tex',
                'deviation_statement': 'deviation_statement.tex',
                'bill_scrutiny': 'bill_scrutiny.tex',
                'extra_items_statement': 'extra_items_statement.tex',
                'certificate_ii': 'certificate_ii.tex',
                'certificate_iii': 'certificate_iii.tex'
            },
            'docx': {
                'summary_report': 'summary_report.docx',
                'detailed_bill': 'detailed_bill.docx',
                'progress_report': 'progress_report.docx'
            }
        }
    
    def setup_ui_config(self):
        """Setup enhanced UI configuration"""
        self.UI = {
            'theme': {
                'primary_color': '#4CAF50',
                'secondary_color': '#66BB6A',
                'accent_color': '#81C784',
                'background_color': '#FFFFFF',
                'secondary_background': '#F0F2F6',
                'text_color': '#262730',
                'success_color': '#4CAF50',
                'warning_color': '#FF9800',
                'error_color': '#F44336',
                'info_color': '#2196F3'
            },
            'layout': {
                'sidebar_width': 350,
                'main_width': 800,
                'max_width': 1400,
                'padding': '2rem',
                'enable_wide_mode': True
            },
            'fonts': {
                'header_font': 'Arial, sans-serif',
                'body_font': 'Roboto, sans-serif',
                'code_font': 'Courier New, monospace',
                'display_font': 'Georgia, serif'
            },
            'animations': {
                'enable_balloons': True,
                'enable_confetti': True,
                'enable_progress_animations': True,
                'transition_duration': '0.3s'
            },
            'icons': {
                'upload': '📁',
                'process': '⚙️',
                'download': '💾',
                'success': '✅',
                'warning': '⚠️',
                'error': '❌',
                'info': 'ℹ️',
                'performance': '⚡',
                'enhanced': '🚀'
            }
        }
    
    def setup_logging(self):
        """Setup enhanced logging configuration"""
        self.LOGGING = {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            'file_handler': {
                'enabled': True,
                'filename': self.DIRS['logs'] / 'billgenerator_enhanced.log',
                'max_bytes': 50 * 1024 * 1024,  # 50MB
                'backup_count': 10
            },
            'console_handler': {
                'enabled': True,
                'colored': True
            },
            'performance_logging': {
                'enabled': True,
                'filename': self.DIRS['logs'] / 'performance.log',
                'track_function_calls': True
            }
        }
    
    def setup_processing_config(self):
        """Setup enhanced data processing configuration"""
        self.PROCESSING = {
            'excel': {
                'sheet_detection': {
                    'title_keywords': ['title', 'cover', 'front', 'project', 'header', 'info'],
                    'work_order_keywords': ['work order', 'work_order', 'workorder', 'wo', 'order'],
                    'bill_quantity_keywords': ['bill quantity', 'bill_quantity', 'billquantity', 'bq', 'quantity', 'bill'],
                    'extra_items_keywords': ['extra items', 'extra_items', 'extraitems', 'extra', 'additional', 'addon']
                },
                'column_mapping': {
                    'flexible_matching': True,
                    'fuzzy_threshold': 0.8,
                    'required_columns': {
                        'item_description': ['description', 'item', 'work description', 'particulars', 'details'],
                        'quantity': ['quantity', 'qty', 'nos', 'number', 'amount'],
                        'unit': ['unit', 'uom', 'unit of measurement', 'measure'],
                        'rate': ['rate', 'unit rate', 'cost', 'price', 'amount'],
                        'amount': ['amount', 'total', 'value', 'cost', 'sum']
                    }
                },
                'validation': {
                    'max_rows': 50000,  # Increased capacity
                    'min_rows': 1,
                    'required_sheets': ['title', 'work_order', 'bill_quantity'],
                    'numeric_precision': 2,
                    'allow_empty_cells': True,
                    'auto_fix_formats': True
                }
            },
            'calculations': {
                'gst_rate': 18.0,
                'rounding_precision': 2,
                'rounding_method': 'standard',
                'currency_symbol': '₹',
                'number_format': 'indian',
                'enable_advanced_calculations': True,
                'auto_calculate_totals': True
            },
            'performance': {
                'batch_size': 1000,
                'enable_parallel_processing': True,
                'memory_optimization': True,
                'cache_results': True
            }
        }
    
    def setup_security_config(self):
        """Setup enhanced security configuration"""
        self.SECURITY = {
            'file_validation': {
                'virus_scan': False,
                'file_type_validation': True,
                'content_validation': True,
                'size_limits': True,
                'extension_whitelist': ['.xlsx', '.xls']
            },
            'data_sanitization': {
                'remove_scripts': True,
                'escape_html': True,
                'validate_formulas': True,
                'sanitize_file_paths': True
            },
            'temporary_files': {
                'auto_cleanup': True,
                'cleanup_interval': 1800,  # 30 minutes
                'max_age': 43200,  # 12 hours
                'secure_deletion': True
            }
        }
    
    def setup_performance_config(self):
        """Setup performance optimization configuration"""
        self.PERFORMANCE = {
            'caching': {
                'enabled': True,
                'default_ttl': 3600,  # 1 hour
                'max_size': 1000,
                'cleanup_interval': 300  # 5 minutes
            },
            'memory': {
                'max_usage_percent': 80,
                'garbage_collection_interval': 100,
                'optimize_dataframes': True
            },
            'processing': {
                'enable_multiprocessing': True,
                'max_workers': 4,
                'chunk_size': 1000,
                'progress_reporting_interval': 10
            }
        }
    
    def setup_cache_config(self):
        """Setup caching configuration from V03"""
        self.CACHE = {
            'memory_cache': {
                'enabled': True,
                'max_size': 500,
                'ttl': 3600
            },
            'file_cache': {
                'enabled': True,
                'directory': self.DIRS['cache'],
                'max_size_mb': 1000,
                'cleanup_interval': 3600
            },
            'redis_cache': {
                'enabled': False,  # Optional Redis support
                'host': 'localhost',
                'port': 6379,
                'db': 0
            }
        }
    
    def _check_latex_availability(self) -> bool:
        """Check if LaTeX is available on the system"""
        try:
            import subprocess
            result = subprocess.run(
                [self.LATEX_ENGINE, '--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False
    
    def get_template_path(self, template_type: str, template_name: str) -> Path:
        """Get full path to template file"""
        if template_type in self.TEMPLATES:
            template_file = self.TEMPLATES[template_type].get(template_name)
            if template_file:
                if template_type == 'latex':
                    return self.DIRS['latex_templates'] / template_file
                else:
                    return self.DIRS['templates'] / template_file
        return None
    
    def get_output_path(self, filename: str) -> Path:
        """Get full path for output file"""
        return self.DIRS['output'] / filename
    
    def get_temp_path(self, filename: str) -> Path:
        """Get full path for temporary file"""
        return self.DIRS['temp'] / filename
    
    def update_config(self, section: str, key: str, value: Any) -> bool:
        """Update configuration value"""
        try:
            if hasattr(self, section.upper()):
                config_section = getattr(self, section.upper())
                if isinstance(config_section, dict) and key in config_section:
                    config_section[key] = value
                    return True
            return False
        except Exception as e:
            logging.error(f"Error updating configuration: {str(e)}")
            return False
    
    def get_config(self, section: str, key: str = None, default: Any = None) -> Any:
        """Get configuration value"""
        try:
            if hasattr(self, section.upper()):
                config_section = getattr(self, section.upper())
                if key is None:
                    return config_section
                elif isinstance(config_section, dict):
                    return config_section.get(key, default)
            return default
        except Exception:
            return default
    
    def save_config(self, filepath: str = None) -> bool:
        """Save current configuration to file"""
        try:
            if filepath is None:
                filepath = self.DIRS['base'] / 'enhanced_config.json'
            
            config_data = {
                'APP_NAME': self.APP_NAME,
                'APP_VERSION': self.APP_VERSION,
                'MAX_FILE_SIZE_MB': self.MAX_FILE_SIZE_MB,
                'LATEX_ENABLED': self.LATEX_ENABLED,
                'UI': self.UI,
                'PROCESSING': self.PROCESSING,
                'SECURITY': self.SECURITY,
                'PERFORMANCE': self.PERFORMANCE,
                'CACHE': self.CACHE
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            logging.error(f"Error saving configuration: {str(e)}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for diagnostics"""
        try:
            import platform
            import sys
            import psutil
            
            return {
                'platform': platform.platform(),
                'python_version': sys.version,
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'cpu_count': psutil.cpu_count(),
                'disk_free': psutil.disk_usage('/').free if os.name != 'nt' else psutil.disk_usage('C:\\').free,
                'latex_available': self.LATEX_ENABLED,
                'app_version': self.APP_VERSION
            }
        except Exception as e:
            logging.error(f"Error getting system info: {str(e)}")
            return {}

# Global enhanced configuration instance
enhanced_config = EnhancedConfig()

# Export main functions
__all__ = ['EnhancedConfig', 'enhanced_config']
