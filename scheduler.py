from datetime import datetime, timedelta
import threading
import time
from mining_service import mining_service
from config import config

class MiningScheduler:
    def __init__(self):
        self.scheduler_thread = None
        self.running = False
    
    def start(self):
        """启动定时任务"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        print("定时任务已启动")
    
    def stop(self):
        """停止定时任务"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("定时任务已停止")
    
    def _scheduler_loop(self):
        """定时任务循环"""
        while self.running:
            # 从配置中获取启动时间
            hour = config['reward_time']['hour']
            minute = config['reward_time']['minute']
            second = config['reward_time']['second']
            
            now = datetime.now()
            # 计算到下一个指定时间的时间
            next_run = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
            if now >= next_run:
                next_run += timedelta(days=1)
            
            wait_seconds = (next_run - now).total_seconds()
            print(f"[{now}] 下次挖矿奖励分发时间: {next_run}, 等待 {wait_seconds} 秒")
            
            # 等待到指定时间
            for _ in range(int(wait_seconds)):
                if not self.running:
                    return
                time.sleep(1)
            
            # 执行挖矿奖励分发
            if self.running:
                try:
                    mining_service.distribute_mining_rewards()
                    mining_service.process_daily_unlock()
                    print(f"[{datetime.now()}] 挖矿奖励分发完成")
                except Exception as e:
                    print(f"定时任务执行失败: {e}")

# 实例化调度器
scheduler = MiningScheduler()