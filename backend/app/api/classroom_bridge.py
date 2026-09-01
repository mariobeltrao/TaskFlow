import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.classroom_bridge import ClassroomBridgeImport, ClassroomBridgeImportResult
from app.services.classroom_bridge_service import ClassroomBridgeService

router = APIRouter(prefix="/integrations/classroom-bridge", tags=["classroom-bridge"])


@router.post("/import", response_model=ClassroomBridgeImportResult)
def import_classroom_events(
    data: ClassroomBridgeImport,
    x_taskflow_bridge_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    expected = get_settings().classroom_bridge_token
    valid = bool(expected and x_taskflow_bridge_token) and hmac.compare_digest(
        x_taskflow_bridge_token.encode(), expected.encode()
    )
    if not valid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bridge token inválido")
    return ClassroomBridgeService(db).import_events(data)
