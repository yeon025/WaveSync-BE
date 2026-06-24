from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models.resonator_master import ResonatorMaster
from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode




def get_resonator_name(db: Session):
    result = db.execute(select(ResonatorMaster.name))

    rows = result.all()

    names = [name for (name,) in rows]

    return names



def validate_resonator(extracted_name, db: Session):
    name_list = get_resonator_name(db)

    for name in name_list:
        if name == extracted_name:
            return
        
    logger.warning(f"공명자 이름이 마스터 데이터에 존재하지 않습니다. resonatorName={extracted_name}")
    raise CustomException(ErrorCode.VALIDATION_FAILED)
