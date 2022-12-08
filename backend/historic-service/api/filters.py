
from .models import TraceModel


def filter_trace(db_query, query_params):
    filtered_query = db_query
    # Filter by date
    date_start_query_param = query_params.get('date_start')
    date_end_query_param = query_params.get('date_end')
    if date_start_query_param and date_end_query_param:
        filtered_query = db_query.filter(TraceModel.date.between(date_start_query_param, date_end_query_param))
    elif date_start_query_param and not date_end_query_param:
        filtered_query = db_query.filter(TraceModel.date >= date_start_query_param)
    elif not date_start_query_param and date_end_query_param:
        filtered_query = db_query.filter(TraceModel.date <= date_end_query_param)
    
    # Filter  by use case
    use_case = query_params.get('use_case')
    if use_case:
        filtered_query = filtered_query.filter(TraceModel.use_case==use_case)
    return filtered_query
