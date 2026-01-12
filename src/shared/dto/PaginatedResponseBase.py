from src.shared.dto.ResponseBase import ResponseBase


class PaginatedResponseBase(ResponseBase):
    current_page: int
    total_pages: int
    page_size: int