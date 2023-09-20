from datetime import datetime, timedelta

def convert_to_timestamp_format(time):
    now = datetime.now()
    time_ext = time.split(' ')[1]
    if time_ext in ['hr',"hrs",'h', "hour"]:
        hours_present = int(time.split(' ')[0])
        now = now - timedelta(hours=hours_present) 
    elif time_ext in ['min','mins']:
        minutes_present = int(time.split(' ')[0])
        now = now - timedelta(minutes=minutes_present)
    elif time_ext in ['day','d','days']:
        days_present = int(time.split(' ')[0])
        now = now - timedelta(days=days_present)
    elif time_ext in ['month','months']:
        print(time.split(' '))
        months_present = int(time.split(' ')[0])
        now = now - timedelta(days=months_present * 30)

    # Format the datetime with .isoformat()  
    current_time = now.isoformat("T") + "Z"

    return current_time
