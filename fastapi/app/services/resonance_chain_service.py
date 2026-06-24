import cv2
from app.config.logger import logger




def _check_chain_level(chain, template):
    threshold=0.95
    
    # 템플릿 매칭 점수 계산
    results = cv2.matchTemplate(chain, template, cv2.TM_CCOEFF_NORMED)
    score = results.max()

    logger.warning(f"score: {score}")

    # 미돌파 템플릿과 유사 → 돌파 안됨
    if score >= threshold:
        return False
    
    # 유사하지 않음 → 돌파됨
    return True






def calculate_chain_level(chain_img_paths, template_path):

    chain_level = 0
    
    template = cv2.imread(template_path)
    
    for chain_path in chain_img_paths:
        chain = cv2.imread(chain_path)
        is_awakened = _check_chain_level(chain, template)
        
        if is_awakened == True:
            chain_level = chain_level + 1
            
    return chain_level