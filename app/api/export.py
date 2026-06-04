"""Excel export endpoint (§5.5 / §5.7): GET /export.xlsx."""

from io import BytesIO

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models import Recibo, Usuario
from app.db.session import get_db
from app.export import excel

router = APIRouter(tags=["export"])

_XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/export.xlsx")
def export_xlsx(
    request: Request,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> StreamingResponse:
    recibos = db.execute(select(Recibo).order_by(Recibo.created_at.desc())).scalars().all()
    content = excel.build_workbook(recibos, str(request.base_url))
    headers = {"Content-Disposition": 'attachment; filename="recibos.xlsx"'}
    return StreamingResponse(BytesIO(content), media_type=_XLSX_MEDIA, headers=headers)
