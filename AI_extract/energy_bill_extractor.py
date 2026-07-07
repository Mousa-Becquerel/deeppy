import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
from datetime import datetime, date
import os
from dataclasses import dataclass
from enum import Enum

from pydantic_ai import Agent, BinaryContent
from pydantic import BaseModel, Field
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_vertex import GoogleVertexProvider
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('energy_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"

class NotElectricityBillError(Exception):
    """Custom exception raised when the document is not an electricity bill"""
    def __init__(self, filename: str, document_type: str = "unknown"):
        self.filename = filename
        self.document_type = document_type
        super().__init__(f"Document '{filename}' is not an electricity bill. Detected type: {document_type}")

@dataclass
class ProcessingResult:
    """Result of processing a single document"""
    filename: str
    status: ProcessingStatus
    data: Optional[Dict] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None

class DocumentValidation(BaseModel):
    """Model for document type validation"""
    is_electricity_bill: bool = Field(..., description="True if this is an electricity/energy bill, False otherwise")
    document_type: str = Field(..., description="Type of document detected (e.g., 'electricity bill', 'gas bill', 'water bill', 'invoice', 'receipt', 'contract', 'other')")
    confidence: float = Field(..., description="Confidence level (0.0 to 1.0) that this classification is correct")
    reason: str = Field(..., description="Brief explanation of why this classification was made")

class Address(BaseModel):
    """Structured address model"""
    street_name: str = Field(..., description="Street name (e.g., Via Roma, Corso Milano)")
    civic_number: str = Field(..., description="Civic/house number (e.g., 123, 45/A)")
    postal_code: str = Field(..., description="Postal/ZIP code (e.g., 00100, 20121)")
    city: str = Field(..., description="City name (e.g., Roma, Milano)")
    province: str = Field(..., description="Province code (e.g., RM, MI, TO)")

class ClientCompany(BaseModel):
    """Enhanced client company model with validation"""
    pod_code: str = Field(..., description="POD (Point of Delivery) code - mandatory field")
    vat_number: Optional[str] = Field(None, description="VAT number of client company only")
    phone_number: Optional[str] = Field(None, description="Client phone number")
    email: Optional[str] = Field(None, description="Client email address")
    name: str = Field(..., description="Client company name")
    address: Address = Field(..., description="Structured client address")
    fiscal_code: Optional[str] = Field(None, description="Client fiscal code")

class NumericWithUnit(BaseModel):
    """Numeric value paired with its unit (€, kWh, kW, Volt, etc.)"""
    value: float = Field(..., description="Numeric value parsed as float")
    unit: str = Field(..., description="Unit of measure, e.g., '€', 'kWh', 'kW', 'Volt'")

class BillDetails(BaseModel):
    """Model to store extracted details about the energy bill."""
    bill_number: str = Field(..., description="Unique identifier for the bill.")
    bill_issue_date: date = Field(..., description="Issue date of the bill as a date (ISO 'YYYY-MM-DD').")
    energy_provider: str = Field(..., description="Name of the energy provider company (e.g., Dolomiti Energia, A2A, Axpo).")
    supply_address: Address = Field(..., description="Structured address where the energy is supplied (POD address).")
    client_type: str = Field(..., description="Type of client (e.g., Altri usi).")
    offer_type: str = Field(..., description="Type of energy offer (e.g., PUN ORARIA).")
    offer_code: str = Field(..., description="Specific code for the energy offer.")
    meter_type: str = Field(..., description="Type of energy meter (e.g., Elettronico gestito orario).")
    billing_frequency: str = Field(..., description="How often the bill is issued (e.g., Mensile).")
    supply_voltage: NumericWithUnit = Field(..., description="Voltage of the electricity supply (e.g., 15000 Volt).")
    committed_power: NumericWithUnit = Field(..., description="Committed power in kW.")
    available_power: NumericWithUnit = Field(..., description="Available power in kW.")
    annual_expense: NumericWithUnit = Field(..., description="Total annual expense related to the supply.")
    annual_total_consumption: NumericWithUnit = Field(..., description="Total annual consumption in kWh.")
    billing_period_start_date: date = Field(..., description="Start date of the current billing period as a date (ISO 'YYYY-MM-DD').")
    billing_period_end_date: date = Field(..., description="End date of the current billing period as a date (ISO 'YYYY-MM-DD').")
    billing_period_f1: NumericWithUnit = Field(..., description="Energy consumption for the current billing period in Fascia F1 (kWh).")
    billing_period_f2: NumericWithUnit = Field(..., description="Energy consumption for the current billing period in Fascia F2 (kWh).")
    billing_period_f3: NumericWithUnit = Field(..., description="Energy consumption for the current billing period in Fascia F3 (kWh).")
    supply_activation_date: str = Field(..., description="Date when the energy supply was activated.")
    contract_expiration_date: str = Field(..., description="Date when the contract expires (or 'A tempo indeterminato').")
    energy_component_cost: NumericWithUnit = Field(..., description="Cost for the energy component.")
    transmission_meter_management_cost: NumericWithUnit = Field(..., description="Cost for transmission and meter management.")
    system_charges_cost: NumericWithUnit = Field(..., description="Cost for system charges.")
    total_taxes_and_iva: NumericWithUnit = Field(..., description="Total amount for taxes and IVA.")
    total_bill_amount: NumericWithUnit = Field(..., description="Total amount of the current bill.")

class CompleteBillExtraction(BaseModel):
    """Complete energy bill extraction combining client and bill details"""
    client_company: ClientCompany = Field(..., description="Client company information")
    bill_details: BillDetails = Field(..., description="Energy bill details and costs")

class EnergyBillExtractor:
    """Production-ready energy bill data extractor"""
    
    def __init__(self, 
                 service_account_file: str = 'alpinvision-55cf56c68e8d.json',
                 region: str = 'europe-west4',
                 project_id: str = 'alpinvision',
                 model_name: str = 'gemini-2.0-flash',
                 max_concurrent: int = 5):
        """
        Initialize the extractor
        
        Args:
            service_account_file: Path to Google Cloud service account JSON
            region: Google Cloud region
            project_id: Google Cloud project ID
            model_name: Gemini model name
            max_concurrent: Maximum concurrent processing tasks
        """
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Document validation prompt
        self.validation_prompt = """You are a document classifier specialized in identifying electricity/energy bills. 
        
        Your task is to determine if the provided document is an electricity or energy bill. Look for these key indicators:
        
        POSITIVE INDICATORS (electricity bill):
        - Energy provider company names (e.g., Enel, Edison, A2A, Dolomiti Energia, Axpo, etc.)
        - Energy consumption measurements (kWh, MW, etc.)
        - POD codes (Punto di Prelievo/Point of Delivery)
        - Electricity tariffs and rates
        - Power supply information (voltage, committed power, available power)
        - Energy meter readings
        - Transmission and distribution costs
        - System charges related to electricity
        - Fascia tariff information (F1, F2, F3)
        - Terms like "fornitura energia elettrica", "bolletta elettrica", "spesa energia"
        
        NEGATIVE INDICATORS (not electricity bill):
        - Gas bills (cubic meters, gas consumption)
        - Water bills (water consumption, sewage)
        - Phone/internet bills (telecom services)
        - General invoices without energy consumption
        - Bank statements
        - Contracts or agreements
        - Insurance documents
        - Tax documents
        
        Be strict in your classification. Only classify as electricity bill if you can clearly identify multiple electricity-specific indicators.
        """
        
        self.system_prompt = """You are an expert assistant specialized in extracting structured information from energy bills. Follow these rules carefully when identifying and extracting the required fields:

        Client Company Details:
        POD Code (Point of Delivery)
        Extract the POD code, which identifies the point of delivery for energy. This field is mandatory.

        VAT Number
        Extract the VAT number of the client only if it exists and only if the client is a company. Do not extract this field if it belongs to the energy service provider or if the client is an individual.

        Client company phone number
        Extract the phone number of the client company only if it exists. Make sure that the number belongs to the client and not to the energy provider or any third-party service company. Avoid including numbers that belong to companies like Dolomiti Energia, A2A, Axpo, or similar providers.

        Client email
        Extract the client's email address only if it exists and clearly belongs to the client. The email must match or relate to the client's name. Make sure that the email is for the client and not for the energy service provider. Exclude any emails that belong to companies such as Dolomiti Energia, A2A, Axpo, or similar. If the email address looks generic or appears unrelated to the client's identity, it should be excluded.

        Client name
        Extract the name of the client exactly as shown on the bill. This should reflect the company's registered name.

        Client Address
        Extract the client address and break it down into structured components:
        - Street name: The street or road name (e.g., "Via Roma", "Corso Milano", "Piazza Garibaldi")
        - Civic number: The house/building number, including any letters or additional identifiers (e.g., "123", "45/A", "67 bis")
        - Postal code: The ZIP/postal code (e.g., "00100", "20121")
        - City: The city name (e.g., "Roma", "Milano", "Torino")
        - Province: The province abbreviation (e.g., "RM", "MI", "TO")

        Fiscal Code
        Extract the fiscal code of the client. Only include it if it clearly refers to the client and not to the energy provider or a third party.

        Bill Details:
        Bill Number
        Extract the unique bill number.

        Bill Issue Date
        Extract the date when this bill was issued (not the billing period). Output in ISO format 'YYYY-MM-DD'. If the bill shows formats like '15/02/2024' or '15-02-2024', convert to '2024-02-15'.

        Energy Provider
        Extract the name of the energy provider company that issued the bill. This could be companies like Dolomiti Energia, A2A, Axpo, Enel, Edison, or any other energy supplier. Look for the company name in headers, logos, or provider identification sections of the bill.

        Supply Address (POD Address)
        Extract the address where the energy is supplied and break it down into structured components. This may be different from the client's billing address:
        - Street name: The street or road name where energy is delivered
        - Civic number: The house/building number for the supply point
        - Postal code: The ZIP/postal code for the supply location
        - City: The city where energy is supplied
        - Province: The province abbreviation for the supply location

        Client Type
        Extract the classification of the client, such as 'Altri usi' (Other uses).

        Offer Type
        Extract the type of energy offer, for example, 'PUN ORARIA'.

        Offer Code
        Extract the specific alphanumeric code identifying the energy offer.

        Meter Type
        Extract the description of the energy meter type, such as 'Elettronico gestito orario'.

        Billing Frequency
        Extract how often the bills are issued, e.g., 'Mensile' (Monthly) or 'Bimestrale' (Bimonthly).

        Supply Voltage
        Extract the voltage of the energy supply, e.g., '15.000 Volt'.

        Committed Power
        Extract the committed power in kW.

        Available Power
        Extract the available power in kW.

        Annual Expense
        Extract the total annual expense incurred, including the period it covers.

        Annual Total Consumption
        Extract the total annual energy consumption in kWh. This is the sum of all energy consumed during the year.

        Billing Period Start Date & End Date
        Extract the start and end dates for the current billing period as two separate fields:
        - billing_period_start_date
        - billing_period_end_date
        Convert any detected date formats from the bill (e.g., '01/01/2024 - 31/01/2024', 'dal 01/01/2024 al 31/01/2024') into ISO format 'YYYY-MM-DD'. For example, '01/02/2024 - 28/02/2024' -> start: '2024-02-01', end: '2024-02-28'.

        Billing Period F1
        Extract the energy consumption for the current billing period in Fascia F1 (peak hours) in kWh. This is the consumption during the current bill period, not annual.

        Billing Period F2
        Extract the energy consumption for the current billing period in Fascia F2 (intermediate hours) in kWh. This is the consumption during the current bill period, not annual.

        Billing Period F3
        Extract the energy consumption for the current billing period in Fascia F3 (off-peak hours) in kWh. This is the consumption during the current bill period, not annual.

        Supply Activation Date
        Extract the date when the energy supply officially began.

        Contract Expiration Date
        Extract the date when the contract is set to expire, or if it is 'A tempo indeterminato' (indefinite).

        Cost for Energy Component
        Extract the amount corresponding to 'Spesa per la materia energia'.

        Cost for Transmission and Meter Management
        Extract the amount corresponding to 'Spesa per il trasporto e la gestione del contatore'.

        Cost for System Charges
        Extract the amount corresponding to 'Spesa per oneri di sistema'.

        Total Taxes and IVA
        Extract the total amount for taxes and IVA. This may appear in different formats:
        - As a single combined line: 'Imposte e IVA 5,32 €'
        - As separate lines: 'Imposte 143,81€' and 'Totale iva 296,45€' - in this case, add them together or extract the sum if already calculated on the bill
        Look for terms like 'Imposte e IVA', 'Totale imposte e IVA', 'Imposte', 'Totale iva', or similar tax-related labels.

        Total Bill Amount
        Extract the final total amount of the bill to be paid, corresponding to 'TOTALE BOLLETTA'.

        Only include fields that are explicitly present and verifiably linked to the client or the bill details. Do not infer or guess missing values. Prioritize accuracy and avoid including data that belongs to energy providers or intermediaries.

        You must output every numeric amount or measurement as an object with two keys: 
        - "value": the numeric part as a float (use dot as decimal separator, no thousand separators)
        - "unit": the textual unit (€, kWh, kW, Volt, etc.)
        For example: {"value": 123.45, "unit": "€"}.
        """
        
        # Initialize the model and agents
        try:
            self.model = GeminiModel(
                model_name,
                provider=GoogleVertexProvider(
                    service_account_file=service_account_file,
                    region=region,
                    project_id=project_id
                ),
            )
            
            # Create validation agent
            self.validation_agent = Agent(self.model, output_type=DocumentValidation, system_prompt=self.validation_prompt)
            
            # Create extraction agent
            self.agent = Agent(self.model, output_type=CompleteBillExtraction, system_prompt=self.system_prompt)
            
            logger.info("EnergyBillExtractor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize extractor: {e}")
            raise
    
    def _jsonable_model_dump(self, model: BaseModel) -> Dict:
        """Return a JSON-serializable dict from a Pydantic model, handling date/datetime."""
        try:
            # Pydantic v2
            return model.model_dump(mode="json")  # dates become ISO strings
        except AttributeError:
            # Fallback (e.g., pydantic v1)
            try:
                raw = model.dict()
            except Exception:
                # Last resort
                return json.loads(json.dumps(model, default=str))

            def convert(obj):
                if isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                if isinstance(obj, list):
                    return [convert(x) for x in obj]
                if isinstance(obj, dict):
                    return {k: convert(v) for k, v in obj.items()}
                return obj

            return convert(raw)

    async def process_single_document(self, file_path: Union[str, Path]) -> ProcessingResult:
        """
        Process a single document
        
        Args:
            file_path: Path to the document file
            
        Returns:
            ProcessingResult object with processing status and data
            
        Raises:
            NotElectricityBillError: If the document is not an electricity bill
        """
        file_path = Path(file_path)
        start_time = datetime.now()
        
        async with self.semaphore:  # Limit concurrent processing
            try:
                logger.info(f"Processing document: {file_path.name}")
                
                # Validate file exists and is readable
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                if not file_path.is_file():
                    raise ValueError(f"Path is not a file: {file_path}")
                
                # Check file size (limit to 10MB)
                file_size = file_path.stat().st_size
                if file_size > 10 * 1024 * 1024:  # 10MB
                    raise ValueError(f"File too large: {file_size} bytes (max 10MB)")
                
                # Determine media type based on file extension
                media_type = self._get_media_type(file_path.suffix.lower())
                
                # Read file data once for both validation and extraction
                file_data = file_path.read_bytes()
                binary_content = BinaryContent(data=file_data, media_type=media_type)
                
                # Step 1: Validate if this is an electricity bill
                logger.info(f"Validating document type for: {file_path.name}")
                validation_result = await self.validation_agent.run([
                    "Please analyze this document and determine if it is an electricity/energy bill.",
                    binary_content
                ])
                
                validation_data = validation_result.output
                logger.info(f"Document validation for {file_path.name}: {validation_data.document_type} (confidence: {validation_data.confidence:.2f})")
                
                # Check if it's an electricity bill
                if not validation_data.is_electricity_bill:
                    raise NotElectricityBillError(
                        filename=file_path.name, 
                        document_type=validation_data.document_type
                    )
                
                # Step 2: If validation passed, proceed with extraction
                logger.info(f"Document validated as electricity bill, proceeding with extraction: {file_path.name}")
                result = await self.agent.run([
                    "Please extract comprehensive structured information from this energy bill, including both client company details and complete bill information.",
                    binary_content
                ])
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                logger.info(f"Successfully processed {file_path.name} in {processing_time:.2f}s")
                
                return ProcessingResult(
                    filename=file_path.name,
                    status=ProcessingStatus.SUCCESS,
                    data=self._jsonable_model_dump(result.output),
                    processing_time=processing_time
                )
                
            except NotElectricityBillError:
                # Re-raise electricity bill validation errors
                raise
            except Exception as e:
                processing_time = (datetime.now() - start_time).total_seconds()
                error_msg = f"Error processing {file_path.name}: {str(e)}"
                logger.error(error_msg)
                
                return ProcessingResult(
                    filename=file_path.name,
                    status=ProcessingStatus.FAILED,
                    error_message=error_msg,
                    processing_time=processing_time
                )
    
    def _get_media_type(self, file_extension: str) -> str:
        """Get media type based on file extension"""
        media_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff'
        }
        
        return media_types.get(file_extension, 'application/octet-stream')
    
    async def process_batch(self, file_paths: List[Union[str, Path]]) -> Dict:
        """
        Process multiple documents in batch
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            Dictionary with processing results and summary
            
        Note:
            Documents that are not electricity bills will be included in failed_extractions
            with the specific error indicating the document type detected.
        """
        start_time = datetime.now()
        logger.info(f"Starting batch processing of {len(file_paths)} documents")
        
        # Process all documents concurrently
        tasks = [self.process_single_document(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Separate successful and failed results
        successful_results = []
        failed_results = []
        
        for result in results:
            if isinstance(result, NotElectricityBillError):
                # Handle electricity bill validation errors
                failed_results.append({
                    'filename': result.filename,
                    'error': str(result),
                    'error_type': 'validation_error',
                    'document_type': result.document_type
                })
            elif isinstance(result, Exception):
                # Handle other exceptions
                failed_results.append({
                    'filename': 'unknown',
                    'error': str(result),
                    'error_type': 'processing_error'
                })
            elif result.status == ProcessingStatus.SUCCESS:
                successful_results.append(result)
            else:
                failed_results.append({
                    'filename': result.filename,
                    'error': result.error_message,
                    'error_type': 'processing_error',
                    'processing_time': result.processing_time
                })
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Create summary
        summary = {
            'total_documents': len(file_paths),
            'successful': len(successful_results),
            'failed': len(failed_results),
            'success_rate': len(successful_results) / len(file_paths) * 100 if file_paths else 0,
            'total_processing_time': total_time,
            'average_time_per_document': total_time / len(file_paths) if file_paths else 0
        }
        
        logger.info(f"Batch processing completed: {summary}")
        
        return {
            'summary': summary,
            'successful_extractions': [
                {
                    'filename': r.filename,
                    'data': r.data,
                    'processing_time': r.processing_time
                } for r in successful_results
            ],
            'failed_extractions': failed_results
        }
    
    def save_results(self, results: Dict, output_file: Union[str, Path]):
        """Save processing results to JSON file"""
        output_file = Path(output_file)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise

# Utility functions for easy integration
async def extract_from_directory(directory_path: str, 
                               output_file: str = None,
                               file_extensions: List[str] = None) -> Dict:
    """
    Extract data from all supported files in a directory
    
    Args:
        directory_path: Path to directory containing documents
        output_file: Optional output file path for results
        file_extensions: List of file extensions to process (default: ['.pdf', '.jpg', '.jpeg', '.png'])
    
    Returns:
        Dictionary with processing results
        
    Note:
        Files that are not electricity bills will be included in the failed_extractions
        with validation errors indicating the detected document type.
    """
    if file_extensions is None:
        file_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif']
    
    directory = Path(directory_path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    # Find all supported files
    file_paths = []
    for ext in file_extensions:
        file_paths.extend(directory.glob(f"*{ext}"))
        file_paths.extend(directory.glob(f"*{ext.upper()}"))
    
    if not file_paths:
        raise ValueError(f"No supported files found in {directory_path}")
    
    logger.info(f"Found {len(file_paths)} files to process")
    
    # Process files
    extractor = EnergyBillExtractor()
    results = await extractor.process_batch(file_paths)
    
    # Save results if output file specified
    if output_file:
        extractor.save_results(results, output_file)
    
    return results

async def extract_from_files(file_paths: List[str], 
                           output_file: str = None) -> Dict:
    """
    Extract data from specific files
    
    Args:
        file_paths: List of file paths to process
        output_file: Optional output file path for results
    
    Returns:
        Dictionary with processing results
        
    Note:
        Files that are not electricity bills will be included in the failed_extractions
        with validation errors indicating the detected document type.
    """
    extractor = EnergyBillExtractor()
    results = await extractor.process_batch(file_paths)
    
    if output_file:
        extractor.save_results(results, output_file)
    
    return results

# Example usage
if __name__ == "__main__":
    async def main():
        # Example 1: Process a directory
        try:
            results = await extract_from_directory(
                directory_path="./energy_bills",
                output_file="extraction_results.json"
            )
            print(f"Processed {results['summary']['total_documents']} documents")
            print(f"Success rate: {results['summary']['success_rate']:.1f}%")
            
            # Show validation errors (non-electricity bills)
            validation_errors = [f for f in results['failed_extractions'] 
                               if f.get('error_type') == 'validation_error']
            if validation_errors:
                print(f"\nNon-electricity bills detected: {len(validation_errors)}")
                for error in validation_errors:
                    print(f"  - {error['filename']}: {error['document_type']}")
                    
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
        
        # Example 2: Process specific files with error handling
        file_list = [
            "bill1.pdf",
            "bill2.pdf", 
            "bill3.jpg"
        ]
        
        try:
            results = await extract_from_files(
                file_paths=file_list,
                output_file="specific_files_results.json"
            )
            print("Specific files processed successfully")
            
            # Handle individual file validation
            for extraction in results['failed_extractions']:
                if extraction.get('error_type') == 'validation_error':
                    print(f"Warning: {extraction['filename']} is not an electricity bill "
                          f"(detected as: {extraction['document_type']})")
                    
        except Exception as e:
            logger.error(f"File processing failed: {e}")
        
        # Example 3: Process single file with explicit error handling
        try:
            extractor = EnergyBillExtractor()
            result = await extractor.process_single_document("sample_bill.pdf")
            print(f"Successfully extracted data from sample_bill.pdf")
        except NotElectricityBillError as e:
            print(f"Error: {e}")
            print(f"Document type detected: {e.document_type}")
        except Exception as e:
            print(f"Processing error: {e}")
    
    # Run the async main function
    asyncio.run(main()) 