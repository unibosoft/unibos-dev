"""
API Views for Documents Module
Handles AJAX requests for OCR processing and pagination
"""

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from decimal import Decimal
import json
import logging

from .models import Document, ProcessingStatus
from .ocr_service import OCRProcessor
from .utils import ThumbnailGenerator
from .thumbnail_service import EnhancedThumbnailGenerator

logger = logging.getLogger('documents.api')


@login_required
def test_structured_data(request, document_id):
    """
    Test endpoint to verify structured data preparation
    """
    from .views import prepare_structured_data, get_receipt_items, get_category_breakdown, check_integration_status
    
    try:
        document = get_object_or_404(Document, id=document_id, user=request.user)
        
        # Prepare structured data
        structured_data = prepare_structured_data(document)
        
        # Get receipt items
        receipt_items = get_receipt_items(document)
        
        # Get category breakdown
        category_breakdown = get_category_breakdown(receipt_items)
        
        # Check integration status
        integration_status = check_integration_status(document)
        
        # Convert Decimal to float for JSON serialization
        def decimal_to_float(obj):
            if hasattr(obj, '__dict__'):
                return {k: decimal_to_float(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, dict):
                return {k: decimal_to_float(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decimal_to_float(item) for item in obj]
            elif isinstance(obj, Decimal):
                return float(obj)
            else:
                return obj
        
        response_data = {
            'success': True,
            'document': {
                'id': document.id,
                'filename': document.original_filename,
                'type': document.document_type,
                'status': document.processing_status,
                'has_ocr_text': bool(document.ocr_text),
                'ocr_text_length': len(document.ocr_text) if document.ocr_text else 0,
                'has_parsed_receipt': hasattr(document, 'parsed_receipt') and document.parsed_receipt is not None
            },
            'structured_data': decimal_to_float(structured_data),
            'items_count': len(receipt_items),
            'category_breakdown': decimal_to_float(category_breakdown),
            'integration_status': integration_status
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error in test_structured_data: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def trigger_ocr(request, document_id):
    """
    Manually trigger OCR processing for a document
    """
    try:
        # Get document
        document = get_object_or_404(Document, id=document_id, user=request.user)
        
        # Check if already processing
        if document.processing_status == 'processing':
            return JsonResponse({
                'success': False,
                'error': 'Document is already being processed'
            }, status=400)
        
        # Update status to processing
        document.processing_status = 'processing'
        document.save()
        
        # Initialize OCR processor
        ocr_processor = OCRProcessor()
        
        # Process OCR
        logger.info(f"Manual OCR triggered for document {document_id}")
        result = ocr_processor.process_document(
            document.file_path.path,
            document_type=document.document_type,
            force_ocr=True,
            document_instance=document
        )
        
        if result['success'] and result.get('ocr_text'):
            # Save OCR results
            document.ocr_text = result['ocr_text']
            document.ocr_confidence = result.get('confidence', 0)
            document.processing_status = 'completed'
            document.ocr_processed_at = timezone.now()
            
            # Update metadata
            if not document.custom_metadata:
                document.custom_metadata = {}
            document.custom_metadata.update({
                'ocr_method': result.get('ocr_method', 'manual'),
                'text_length': len(result['ocr_text']),
                'manual_trigger': True,
                'processing_time': str(timezone.now())
            })
            
            document.save()
            
            # Parse receipt data if applicable
            if document.document_type == 'receipt' and result.get('parsed_data'):
                from .views import DocumentUploadView
                view = DocumentUploadView()
                view.save_parsed_receipt(document, result['parsed_data'])
            
            return JsonResponse({
                'success': True,
                'message': f'OCR completed successfully. Extracted {len(result["ocr_text"])} characters.',
                'data': {
                    'ocr_text': result['ocr_text'][:500] + '...' if len(result['ocr_text']) > 500 else result['ocr_text'],
                    'confidence': result.get('confidence', 0),
                    'text_length': len(result['ocr_text'])
                }
            })
        else:
            # OCR failed
            document.processing_status = 'failed'
            document.custom_metadata = {
                'ocr_error': result.get('error', 'No text extracted'),
                'manual_trigger': True,
                'failed_at': str(timezone.now())
            }
            document.save()
            
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Failed to extract text from document'),
                'message': 'OCR processing failed. Please try again or review the document manually.'
            }, status=400)
            
    except Exception as e:
        logger.error(f"Manual OCR trigger failed for document {document_id}: {str(e)}")
        
        # Reset document status
        if 'document' in locals():
            document.processing_status = 'failed'
            document.save()
        
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'An unexpected error occurred during OCR processing'
        }, status=500)


@login_required
def get_document_status(request, document_id):
    """
    Get the current processing status of a document
    """
    try:
        document = get_object_or_404(Document, id=document_id, user=request.user)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': str(document.id),
                'status': document.processing_status,
                'status_display': document.get_processing_status_display(),
                'has_ocr': bool(document.ocr_text),
                'ocr_confidence': document.ocr_confidence,
                'ocr_text_preview': document.ocr_text[:200] + '...' if document.ocr_text and len(document.ocr_text) > 200 else document.ocr_text,
                'thumbnail_url': document.thumbnail_path.url if document.thumbnail_path else None,
                'processed_at': document.ocr_processed_at.isoformat() if document.ocr_processed_at else None
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def batch_trigger_ocr(request):
    """
    Trigger OCR for multiple documents
    """
    try:
        # Get document IDs from request
        document_ids = json.loads(request.body).get('document_ids', [])
        
        if not document_ids:
            return JsonResponse({
                'success': False,
                'error': 'No documents selected'
            }, status=400)
        
        # Validate ownership
        documents = Document.objects.filter(
            id__in=document_ids,
            user=request.user,
            processing_status__in=['pending', 'failed', 'manual_review']
        )
        
        if not documents.exists():
            return JsonResponse({
                'success': False,
                'error': 'No valid documents found for processing'
            }, status=400)
        
        # Process each document
        ocr_processor = OCRProcessor()
        results = {
            'processed': 0,
            'failed': 0,
            'errors': []
        }
        
        for document in documents:
            try:
                # Update status
                document.processing_status = 'processing'
                document.save()
                
                # Process OCR
                result = ocr_processor.process_document(
                    document.file_path.path,
                    document_type=document.document_type,
                    force_ocr=True,
                    document_instance=document
                )
                
                if result['success'] and result.get('ocr_text'):
                    document.ocr_text = result['ocr_text']
                    document.ocr_confidence = result.get('confidence', 0)
                    document.processing_status = 'completed'
                    document.ocr_processed_at = timezone.now()
                    document.save()
                    results['processed'] += 1
                else:
                    document.processing_status = 'failed'
                    document.save()
                    results['failed'] += 1
                    results['errors'].append(f"{document.original_filename}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                document.processing_status = 'failed'
                document.save()
                results['failed'] += 1
                results['errors'].append(f"{document.original_filename}: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'message': f"Processed {results['processed']} documents, {results['failed']} failed",
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Batch OCR trigger failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def regenerate_thumbnail(request, document_id):
    """
    Regenerate thumbnail for a document with enhanced cropping
    """
    try:
        document = get_object_or_404(Document, id=document_id, user=request.user)
        
        # Check if source file exists
        if not document.file_path:
            return JsonResponse({
                'success': False,
                'error': 'Source document file not found'
            }, status=404)
        
        # Use enhanced thumbnail generator
        thumbnail_generator = EnhancedThumbnailGenerator()
        thumb_file = thumbnail_generator.generate_from_django_file(
            document.file_path,
            f"thumb_{document.id}.jpg"
        )
        
        if thumb_file:
            # Delete old thumbnail if exists
            if document.thumbnail_path:
                try:
                    document.thumbnail_path.delete(save=False)
                except:
                    pass  # Ignore deletion errors
            
            # Save new thumbnail
            document.thumbnail_path.save(f"thumb_{document.id}.jpg", thumb_file)
            document.save()
            
            logger.info(f"Thumbnail regenerated for document {document_id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Thumbnail regenerated successfully',
                'data': {
                    'thumbnail_url': document.thumbnail_path.url,
                    'document_id': str(document.id)
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to generate thumbnail'
            }, status=400)
            
    except Exception as e:
        logger.error(f"Thumbnail regeneration failed for document {document_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def batch_regenerate_thumbnails(request):
    """
    Regenerate thumbnails for multiple documents
    """
    try:
        # Get parameters
        data = json.loads(request.body) if request.body else {}
        document_ids = data.get('document_ids', [])
        regenerate_all = data.get('all', False)
        force = data.get('force', False)
        
        # Get documents queryset
        if regenerate_all:
            documents = Document.objects.filter(user=request.user)
        elif document_ids:
            documents = Document.objects.filter(user=request.user, id__in=document_ids)
        else:
            # Regenerate for documents without thumbnails
            documents = Document.objects.filter(
                user=request.user,
                thumbnail_path__isnull=True
            )
        
        # Use enhanced thumbnail generator
        generator = EnhancedThumbnailGenerator()
        results = generator.regenerate_all_thumbnails(documents, force=force)
        
        return JsonResponse({
            'success': True,
            'message': f"Processed {results['success']} thumbnails successfully",
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Batch thumbnail regeneration failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def ai_batch_process(request):
    """
    Process documents with AI enhancement for better OCR understanding
    """
    try:
        # Get parameters
        data = json.loads(request.body) if request.body else {}
        document_ids = data.get('document_ids', [])
        all_documents = data.get('all_documents', False)
        
        # Get documents to process
        if all_documents:
            # Process all user's documents without AI processing
            documents = Document.objects.filter(
                user=request.user,
                ai_processed=False
            ).exclude(ocr_text__isnull=True).exclude(ocr_text='')
        elif document_ids:
            documents = Document.objects.filter(
                user=request.user,
                id__in=document_ids
            )
        else:
            # Process pending documents
            documents = Document.objects.filter(
                user=request.user,
                ai_processed=False,
                processing_status='completed'
            ).exclude(ocr_text__isnull=True).exclude(ocr_text='')[:50]  # Limit to 50 for safety
        
        # Initialize OCR processor with AI
        from .ocr_service import OCRProcessor
        processor = OCRProcessor()
        
        if not processor.ai_enhancer:
            return JsonResponse({
                'success': False,
                'error': 'AI enhancer not available. Please set HUGGINGFACE_API_KEY environment variable.'
            }, status=400)
        
        # Process documents
        document_ids = list(documents.values_list('id', flat=True))
        
        # Define progress callback
        def progress_callback(current, total, message=""):
            # In a real implementation, this could update a cache or websocket
            logger.info(f"AI Processing: {current}/{total} - {message}")
        
        # Run batch AI processing
        results = processor.batch_ai_process(document_ids, progress_callback)
        
        return JsonResponse(results)
        
    except Exception as e:
        logger.error(f"AI batch processing failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def search_documents(request):
    """
    Search documents with live results
    """
    try:
        query = request.GET.get('q', '')
        doc_type = request.GET.get('type', '')
        limit = int(request.GET.get('limit', 10))
        
        # Build query
        documents = Document.objects.filter(user=request.user)
        
        if query:
            documents = documents.filter(
                models.Q(original_filename__icontains=query) |
                models.Q(ocr_text__icontains=query) |
                models.Q(parsed_receipt__store_name__icontains=query)
            )
        
        if doc_type:
            documents = documents.filter(document_type=doc_type)
        
        # Limit results
        documents = documents[:limit]
        
        # Prepare results
        results = []
        for doc in documents:
            result = {
                'id': str(doc.id),
                'filename': doc.original_filename,
                'type': doc.get_document_type_display(),
                'status': doc.get_processing_status_display(),
                'uploaded_at': doc.uploaded_at.isoformat(),
                'has_ocr': bool(doc.ocr_text),
                'thumbnail_url': doc.thumbnail_path.url if doc.thumbnail_path else None
            }
            
            # Add receipt data if available
            if hasattr(doc, 'parsed_receipt'):
                result['store_name'] = doc.parsed_receipt.store_name
                result['total_amount'] = str(doc.parsed_receipt.total_amount) if doc.parsed_receipt.total_amount else None
            
            results.append(result)
        
        return JsonResponse({
            'success': True,
            'data': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Document search failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def get_processing_status(request):
    """
    Get current processing status for live updates
    Returns stats and currently processing document
    """
    try:
        from django.db.models import Q, Count

        # Get stats
        stats = Document.objects.filter(user=request.user, is_deleted=False).aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(processing_status='pending')),
            processing=Count('id', filter=Q(processing_status='processing')),
            completed=Count('id', filter=Q(processing_status='completed')),
            failed=Count('id', filter=Q(processing_status='failed'))
        )

        # Get currently processing document
        current_doc = Document.objects.filter(
            user=request.user,
            is_deleted=False,
            processing_status='processing'
        ).order_by('uploaded_at').first()

        response_data = {
            'success': True,
            'stats': {
                'total': stats['total'],
                'pending': stats['pending'],
                'processing': stats['processing'],
                'completed': stats['completed'],
                'failed': stats['failed']
            }
        }

        if current_doc:
            # Get thumbnail URL
            thumbnail_url = None
            if current_doc.thumbnail_path:
                thumbnail_url = current_doc.thumbnail_path.url

            response_data['current_processing'] = {
                'id': str(current_doc.id),
                'filename': current_doc.original_filename,
                'uploaded_at': current_doc.uploaded_at.strftime('%d %b %Y %H:%M'),
                'thumbnail_url': thumbnail_url
            }
        else:
            response_data['current_processing'] = None

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Get processing status failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def ocr_pause(request):
    """
    Pause background OCR processing
    """
    try:
        from django.core.cache import cache
        cache.set('ocr_processing_paused', True, timeout=None)

        logger.info(f"OCR processing paused by user {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': 'OCR processing paused',
            'is_paused': True
        })
    except Exception as e:
        logger.error(f"OCR pause failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def ocr_resume(request):
    """
    Resume background OCR processing
    """
    try:
        from django.core.cache import cache
        cache.delete('ocr_processing_paused')

        logger.info(f"OCR processing resumed by user {request.user.username}")

        return JsonResponse({
            'success': True,
            'message': 'OCR processing resumed',
            'is_paused': False
        })
    except Exception as e:
        logger.error(f"OCR resume failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def ocr_status(request):
    """
    Get current OCR processing pause status
    """
    try:
        from django.core.cache import cache
        is_paused = cache.get('ocr_processing_paused', False)

        return JsonResponse({
            'success': True,
            'is_paused': is_paused
        })
    except Exception as e:
        logger.error(f"OCR status check failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)