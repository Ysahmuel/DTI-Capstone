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

from .excel_views import (
    UploadExcelView,
    ExportDocumentsExcelView,
    ProcessUploadView,
    UploadProgressStreamView,
    CancelUploadView,
)

from .action_views import (
    ApproveDocumentsView
)

from .pdf_views import (
    view_oop,
    )