import re

def validate_id_number(id_number):
    """
    验证大陆身份证号是否正确
    :param id_number: 待验证的身份证号
    :return: True表示身份证号格式正确，False表示身份证号格式不正确
    """
    if not isinstance(id_number, str):
        return False
    id_number = id_number.strip()
    if len(id_number) != 18:
        return False
    if not re.match(r'^\d{17}(\d|X)$', id_number):
        return False
    # 下面是计算身份证号是否有效的代码
    id_list = list(id_number)
    factor = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_code_list = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    check_sum = 0
    for i in range(17):
        check_sum += int(id_list[i]) * factor[i]
    check_code = check_code_list[check_sum % 11]
    if id_list[-1] != check_code:
        return False
    return True