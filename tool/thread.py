import configSetting

def generateThreadWorkers(taskNumbers: int) -> int:
    thread_workers = int(taskNumbers ** 0.5) * 2
    if thread_workers >= configSetting.multithread_high:
        thread_workers = configSetting.multithread_high
    elif thread_workers >= configSetting.multithread_median:
        thread_workers = configSetting.multithread_median

    return thread_workers