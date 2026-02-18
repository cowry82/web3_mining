from datetime import datetime, timedelta
from typing import Optional


class TimeUtils:
    # 时间工具类，提供各种时间相关的辅助方法
    
    @staticmethod
    def get_utc8_now() -> datetime:
        # 获取当前UTC+8时间（北京时间）
        return datetime.utcnow() + timedelta(hours=8)

    @staticmethod
    def is_distribution_time(current_time: Optional[datetime] = None) -> bool:
        # 判断当前时间是否是奖励分发时间（每天00:00:00）
        if current_time is None:
            current_time = TimeUtils.get_utc8_now()
        
        return current_time.hour == 0 and current_time.minute == 0 and current_time.second == 0

    @staticmethod
    def get_next_distribution_time(current_time: Optional[datetime] = None) -> datetime:
        # 获取下一次奖励分发时间（下一天的00:00:00）
        if current_time is None:
            current_time = TimeUtils.get_utc8_now()
        
        next_day = current_time + timedelta(days=1)
        return datetime(next_day.year, next_day.month, next_day.day, 0, 0, 0)

    @staticmethod
    def get_start_of_day(date: Optional[datetime] = None) -> datetime:
        # 获取指定日期的开始时间（00:00:00）
        if date is None:
            date = TimeUtils.get_utc8_now()
        
        return datetime(date.year, date.month, date.day, 0, 0, 0)

    @staticmethod
    def get_end_of_day(date: Optional[datetime] = None) -> datetime:
        # 获取指定日期的结束时间（23:59:59）
        if date is None:
            date = TimeUtils.get_utc8_now()
        
        return datetime(date.year, date.month, date.day, 23, 59, 59)

    @staticmethod
    def days_between(start_date: datetime, end_date: datetime) -> int:
        # 计算两个日期之间的天数
        return (end_date - start_date).days

    @staticmethod
    def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
        # 格式化日期时间为字符串
        return dt.strftime(format_str)
