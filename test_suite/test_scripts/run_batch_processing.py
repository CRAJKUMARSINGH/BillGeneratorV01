#!/usr/bin/env python3
"""
Command-line script for running batch processing
Addresses the performance issues and enables efficient batch processing
"""

import os
import sys
import time
import argparse
from pathlib import Path
import logging

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from batch_processor import HighPerformanceBatchProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function for command-line batch processing"""
    parser = argparse.ArgumentParser(
        description="High-Performance Batch Processor for Bill Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_batch_processing.py input_files
  python run_batch_processing.py input_files -o output_dir
  python run_batch_processing.py input_files -m parallel -w 6
  python run_batch_processing.py input_files --validate
        """
    )
    
    parser.add_argument(
        "input_dir",
        help="Input directory containing Excel files to process"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="batch_output",
        help="Output directory for processed files (default: batch_output)"
    )
    
    parser.add_argument(
        "-m", "--mode",
        choices=["sequential", "parallel"],
        default="parallel",
        help="Processing mode (default: parallel)"
    )
    
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate output quality and report issues"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Validate input directory
    input_path = Path(args.input_dir)
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_path}")
        sys.exit(1)
    
    if not input_path.is_dir():
        logger.error(f"Input path is not a directory: {input_path}")
        sys.exit(1)
    
    # Check for Excel files
    excel_files = list(input_path.glob("*.xlsx")) + list(input_path.glob("*.xls"))
    if not excel_files:
        logger.error(f"No Excel files found in {input_path}")
        sys.exit(1)
    
    logger.info(f"Found {len(excel_files)} Excel files to process")
    
    # Create output directory
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize processor
    processor = HighPerformanceBatchProcessor(str(input_path), str(output_path))
    
    # Progress callback
    def progress_callback(message: str):
        logger.info(message)
    
    # Process files
    start_time = time.time()
    
    try:
        if args.mode == "sequential":
            logger.info("Starting sequential processing...")
            results = processor.process_batch_sequential(progress_callback)
        else:
            logger.info(f"Starting parallel processing with {args.workers} workers...")
            results = processor.process_batch_parallel(args.workers, progress_callback)
        
        # Generate report
        report = processor.generate_batch_report(results)
        
        # Save report
        report_path = output_path / f"batch_report_{int(time.time())}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Print summary
        stats = results['stats']
        logger.info("=" * 60)
        logger.info("BATCH PROCESSING COMPLETED")
        logger.info("=" * 60)
        logger.info(f"Total Files: {stats['total_files']}")
        logger.info(f"Successfully Processed: {stats['processed_files']}")
        logger.info(f"Failed: {stats['failed_files']}")
        logger.info(f"Success Rate: {(stats['processed_files'] / stats['total_files'] * 100):.1f}%")
        logger.info(f"Total Time: {stats['total_time']:.2f} seconds")
        logger.info(f"Average Time per File: {(stats['total_time'] / stats['total_files']):.2f} seconds")
        
        if stats['output_sizes']:
            total_size = sum(stats['output_sizes'])
            avg_size = total_size / len(stats['output_sizes'])
            logger.info(f"Total Output Size: {total_size:,} bytes")
            logger.info(f"Average Output Size: {avg_size:,.0f} bytes")
        
        logger.info(f"Report saved to: {report_path}")
        
        # Quality validation
        if args.validate:
            logger.info("\n" + "=" * 60)
            logger.info("QUALITY VALIDATION")
            logger.info("=" * 60)
            
            quality_issues = []
            for result in results['results']:
                if result['success']:
                    # Check file size (should be > 10KB for proper PDFs)
                    if result['output_size'] < 10240:
                        quality_issues.append(f"{result['file_name']}: Small output size ({result['output_size']} bytes)")
                    
                    # Check processing time (should be reasonable)
                    if result['processing_time'] > 30:
                        quality_issues.append(f"{result['file_name']}: Slow processing ({result['processing_time']:.2f}s)")
            
            if quality_issues:
                logger.warning("Quality Issues Detected:")
                for issue in quality_issues:
                    logger.warning(f"  • {issue}")
            else:
                logger.info("✅ All outputs meet quality standards!")
        
        # Exit with appropriate code
        if stats['failed_files'] > 0:
            logger.warning(f"Processing completed with {stats['failed_files']} failures")
            sys.exit(1)
        else:
            logger.info("✅ All files processed successfully!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("\nProcessing interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
