from .create_views import (
    CreateSalesPromotionView,
    CreatePersonalDataSheetView,
    CreateServiceRepairAccreditationApplicationView,
    CreateInspectionValidationReportView,
    CreateOrderOfPaymentView,
    CreateChecklistEvaluationSheetView,
)
from .detail_views import (
    SalesPromotionDetailView,
    PersonalDataSheetDetailView,
    ServiceRepairAccreditationApplicationDetailView,
    InspectionValidationReportDetailView,
    OrderOfPaymentDetailView,
    ChecklistEvaluationSheetDetailView,
    CollectionReportDetailView,
    CollectionReportItemDetailView,
)

from .update_views import (
    UpdateSalesPromotionView,
    UpdatePersonalDataSheetView,
    UpdateServiceRepairAccreditationApplicationView,
    UpdateInspectionValidationReportView,
    UpdateOrderOfPaymentView,
    UpdateChecklistEvaluationSheetView
)

from .list_views import (
    AllDocumentListView,
    SalesPromotionListView,
    PersonalDataSheetListView,
    ServiceRepairAccreditationApplicationListView,
    InspectionValidationReportListView,
    OrderOfPaymentListView,
    ChecklistEvaluationSheetListView,
    CollectionReportListView,
)

from .upload_excel_views import (
    UploadExcelView,
    ProcessUploadView,
    UploadProgressStreamView,
    CancelUploadView,
)

from .export_report_views import (
    ExportDocumentsExcelView
)

from .action_views import (
    ApproveDocumentsView
)


from .pdf_views import (
    view_oop,
    )