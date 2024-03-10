from sqlalchemy_file.validators import Validator, SizeValidationError, ContentTypeValidationError
from typing import Union, TYPE_CHECKING, Optional, List
from sqlalchemy_file.helpers import convert_size

if TYPE_CHECKING:
    from sqlalchemy_file.file import File


class CustomSizeValidator(Validator):
    def __init__(self, max_size: Union[int, str] = 0) -> None:
        super().__init__()
        self.max_size = max_size

    def process(self, file: "File", attr_key: str) -> None:
        if file.size > convert_size(self.max_size):
            raise SizeValidationError(
                attr_key,
                msg=f'Файл {file.filename} слишком велик ({file.size} байт). Разрешенный размер - {self.max_size}'
            )


class CustomContentTypeValidator(Validator):
    def __init__(self, allowed_content_types: Optional[List[str]] = None) -> None:
        super().__init__()
        self.allowed_content_types = allowed_content_types

    def process(self, file: "File", attr_key: str) -> None:
        if (
                self.allowed_content_types is not None
                and file.content_type not in self.allowed_content_types
        ):
            raise ContentTypeValidationError(
                attr_key,
                f"Тип файла {file.filename} не разрешен. Разрешенные типы файлов: {self.allowed_content_types}",
            )
