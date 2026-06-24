from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models.weapon_master import WeaponMaster
from app.config.logger import logger
from app.exceptions.custom_exception import CustomException
from app.exceptions.error_code import ErrorCode






def get_weapon_name(db: Session):
    result = db.execute(select(WeaponMaster.name))

    rows = result.all()

    return [name for (name,) in rows]



def validate_weapon(extracted_name, db: Session):
    name_list = get_weapon_name(db)

    for name in name_list:
        name_without_spaces = name.replace(" ", "")
        if name_without_spaces == extracted_name:
            return name
        
    logger.warning(f"무기 이름이 마스터 데이터에 존재하지 않습니다. weaponName={extracted_name}")
    raise CustomException(ErrorCode.VALIDATION_FAILED)
